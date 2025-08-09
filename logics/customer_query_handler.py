# customer_query_handler.py

import streamlit as st
import json
import os
from openai import OpenAI
from collections import deque
import re
import faiss
import numpy as np
# Fix for LangChainDeprecationWarning - using the updated import
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# --- 1. Load Environment Variables & Initialize OpenAI Client ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 2. Global Variables (Existing and New FAISS-related) ---
dict_of_courses_structured = {}
global_last_discussed_course_name = None
MAX_HISTORY_LENGTH = 5
conversation_history = deque(maxlen=MAX_HISTORY_LENGTH)

# FAISS related globals
faiss_index = None
course_chunks_metadata = []
embeddings_model = None

# Configuration for FAISS paths (must match build_faiss_index.py)
FAISS_INDEX_PATH = 'data/faiss_index.bin'
METADATA_PATH = 'data/faiss_metadata.json'
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"

# --- 3. Data Loading Functions (Existing and New FAISS Loading) ---
def load_structured_course_data(json_file_path='data/specialist_diploma_programmes.json'):
    """
    Loads structured course data from a JSON file and populates the global dictionary.
    This revised version now uses the full title as the dictionary key to ensure a match.
    """
    global dict_of_courses_structured
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            print("Structured course data is a list. Processing each item...")
            for item in data:
                course_title_full = item.get('title')
                if course_title_full:
                    # Initialize with default None values
                    course_details = {
                        'name': course_title_full,  # Use the full title for the 'name' field
                        'url': item.get('url', ''),
                        'description': item.get('description', ''),
                        'category': None,
                        'price': None,
                        'duration': None,
                        'skills_covered': None,
                        'entry_requirements': None,
                        'course_schedule': None,
                        'provider': None,
                        'course_code': None
                    }
                    
                    # --- REVISED LOGIC: Parse details from title and description ---
                    # 1. Extract a course code using a regex pattern that also includes acronyms
                    course_code_match = re.search(r'\b[A-Z]{2,5}\d{2,5}\b', course_title_full)
                    if course_code_match:
                        course_details['course_code'] = course_code_match.group(0).strip()
                    else:
                        # NEW: Try to extract a common acronym like SDBIM, SDCM, etc.
                        acronym_match = re.search(r'\(([A-Z]{3,5})\)', course_title_full)
                        if acronym_match:
                            course_details['course_code'] = acronym_match.group(1).strip()
                    
                    # 2. Try to extract duration from description
                    duration_match = re.search(r'(\d+)\s*(?:month|year)s?\b', item.get('description', ''), re.IGNORECASE)
                    if duration_match:
                        course_details['duration'] = duration_match.group(0).strip()
                    # --- END REVISED LOGIC ---

                    # --- CRITICAL FIX: Use the full title as the dictionary key
                    dict_of_courses_structured[course_title_full] = course_details

        elif isinstance(data, dict):
            print("Structured course data is a dictionary. Processing key-value pairs...")
            for course_name, details in data.items():
                dict_of_courses_structured[course_name] = {
                    'name': details.get('name'),
                    'overview': details.get('overview'),
                    'duration': details.get('duration'),
                    'fees': details.get('fees'),
                    'entry_requirements': details.get('entry_requirements'),
                    'skills_gained': details.get('skills_gained'),
                    'career_opportunities': details.get('career_opportunities'),
                    'intake': details.get('intake')
                }
        print("Structured course data loaded successfully.")
    except FileNotFoundError:
        st.error(f"Error: Structured course data file not found at {json_file_path}. Please ensure it exists.")
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode JSON from {json_file_path}. Check file format.")

def load_faiss_components():
    global faiss_index, course_chunks_metadata, embeddings_model

    if faiss_index is not None and embeddings_model is not None:
        print("FAISS components already loaded.")
        return

    print(f"Initializing embedding model for query: {EMBEDDING_MODEL_NAME}...")
    try:
        embeddings_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
        print("Embedding model initialized.")
    except Exception as e:
        st.error(f"Error initializing embedding model: {e}. Check your OPENAI_API_KEY and network.")
        return

    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
        try:
            print(f"Loading FAISS index from {FAISS_INDEX_PATH} and metadata from {METADATA_PATH}...")
            faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                course_chunks_metadata = json.load(f)
            print("FAISS index and metadata loaded successfully.")
        except Exception as e:
            st.error(f"Error loading FAISS components: {e}. Please ensure you've run 'build_faiss_index.py' and the files exist.")
    else:
        st.error(f"FAISS index or metadata not found. Expected at '{FAISS_INDEX_PATH}' and '{METADATA_PATH}'.")
        st.error("Please run the 'build_faiss_index.py' script once to generate them before starting the app.")

# --- 4. REVISED: Web Scraping Function to fetch structured content from URL ---
def fetch_url_content(url):
    """
    Fetches and scrapes text content from a given URL, prioritizing structured data.
    Returns the scraped text or an empty string on failure.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        relevant_text = []

        # Scrape headings and paragraphs
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li']):
            text = tag.get_text(strip=True)
            if text:
                relevant_text.append(text)
        
        # Scrape tables specifically, as fee information is often in tables
        for table in soup.find_all('table'):
            table_text = []
            for row in table.find_all('tr'):
                row_text = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if row_text:
                    table_text.append("|".join(row_text))
            if table_text:
                relevant_text.append("--- TABLE DATA ---\n" + "\n".join(table_text) + "\n--- END TABLE DATA ---")
        
        scraped_text = "\n".join(relevant_text)
        
        # 🐛 DEBUGGING LINE: Print scraped content to terminal
        print(f"--- START SCRAPED CONTENT FROM {url} ---")
        print(scraped_text)
        print(f"--- END SCRAPED CONTENT FROM {url} ---")
        
        return scraped_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""
    except Exception as e:
        print(f"Error scraping content from {url}: {e}")
        return ""

def get_url_from_course_name(course_name):
    """Retrieves the URL for a given course name from the structured data."""
    course_info = dict_of_courses_structured.get(course_name)
    return course_info.get('url') if course_info else None

# --- 5. LLM Helper Function ---
def get_llm_response(prompt_messages):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=prompt_messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        if "AuthenticationError" in str(e):
            return "I apologize, but there's an issue with the API key. Please ensure it's correct."
        return f"I apologize, but I encountered an error communicating with the AI: {e}"

# --- 6. Intent Recognition & Extraction Functions ---
def identify_user_intent(query, history=None):
    query_lower = query.lower()
    if "recommend" in query_lower or "suggest" in query_lower or "suitable for" in query_lower:
        return "recommendation"
    elif any(keyword in query_lower for keyword in ["fee", "cost", "price", "charge"]):
        return "specific_detail_fees"
    elif any(keyword in query_lower for keyword in ["entry", "requirements", "prerequisite"]):
        return "specific_detail_entry_requirements"
    elif any(keyword in query_lower for keyword in ["schedule", "intake", "start date", "duration"]):
        return "specific_detail_schedule"
    elif any(course_name.lower() in query_lower for course_name in dict_of_courses_structured):
        return "specific_course_info"
    return "general_info"

def extract_course_name_from_query(query):
    for course_name in dict_of_courses_structured:
        # Use a more robust regex to match the full course name or its acronym
        match = re.search(r'\b(?:' + re.escape(course_name) + r'|' + re.escape(dict_of_courses_structured[course_name].get('course_code', '')) + r')\b', query, re.IGNORECASE)
        if match:
            return course_name
    return None

# --- 7. Core Query Handling (Modified to use FAISS + Web Scraping) ---
def process_user_message(user_query: str):
    global global_last_discussed_course_name, conversation_history

    if faiss_index is None:
        load_faiss_components()
        if faiss_index is None:
            return "I'm sorry, my knowledge base could not be loaded. Please ensure all setup steps are complete.", [], False
    if embeddings_model is None:
        return "I'm sorry, the embedding model is not initialized.", [], False

    try:
        # --- NEW: Dynamically enrich the user query for broader search ---
        enriched_query = user_query
        if "project managers" in user_query.lower():
            enriched_query += " construction management BIM management"
        
        query_embedding = embeddings_model.embed_query(enriched_query)
        query_embedding_np = np.array([query_embedding]).astype('float32')
    except Exception as e:
        return f"Error embedding your query: {e}. Cannot perform search.", [], False

    k = 5
    distances, indices = faiss_index.search(query_embedding_np, k)

    retrieved_context = []
    retrieved_course_names = set()
    retrieved_urls_with_names = {} # Use a dictionary to store unique URLs with course names

    for i in indices[0]:
        if i != -1 and i < len(course_chunks_metadata):
            chunk_info = course_chunks_metadata[i]
            retrieved_context.append(chunk_info["chunk"])
            retrieved_course_names.add(chunk_info["original_item_title"])
            
            # --- FIX: Store URL and course name together
            course_name = chunk_info["original_item_title"]
            url = chunk_info["url"]
            if course_name not in retrieved_urls_with_names:
                retrieved_urls_with_names[course_name] = url

    context_str = "\n---\n".join(retrieved_context)

    dynamic_context = ""
    course_url_for_details = None
    
    specific_detail_keywords = ["fee", "cost", "price", "charge", "entry", "requirements", "prerequisite", "schedule", "intake", "start date", "duration", "course dates"]
    has_specific_query = any(keyword in user_query.lower() for keyword in specific_detail_keywords)

    # --- FIX: Prioritize explicit course name from user query for follow-ups ---
    explicit_course_name = extract_course_name_from_query(user_query)
    if explicit_course_name:
        global_last_discussed_course_name = explicit_course_name
        
    if has_specific_query and global_last_discussed_course_name:
        course_url_for_details = get_url_from_course_name(global_last_discussed_course_name)
    elif retrieved_course_names:
        first_course_name = next(iter(retrieved_course_names), None)
        if first_course_name:
            course_url_for_details = get_url_from_course_name(first_course_name)

    if course_url_for_details:
        print(f"Fetching details from {course_url_for_details}...")
        scraped_content = fetch_url_content(course_url_for_details)
        if scraped_content:
            dynamic_context = f"\n\n--- Dynamically Scraped Content from {course_url_for_details} ---\n{scraped_content}\n"
            print("Successfully scraped content. Adding to context.")
        else:
            print(f"Failed to scrape content from {course_url_for_details}. Relying on static context.")

    final_context = context_str + dynamic_context

    if not final_context:
        return "I couldn't find relevant information in my knowledge base. Please try rephrasing or ask about specific BCA Academy Specialist Diploma programmes.", [], has_specific_query
    
    # --- UPDATED LOGIC: Use more specific and structured prompts for different queries
    if has_specific_query and dynamic_context:
        # Check for schedule query and use a specific prompt
        if any(keyword in user_query.lower() for keyword in ["schedule", "intake", "start date", "duration", "course dates"]):
            system_prompt = f"""
            You are a helpful AI assistant. Your task is to extract all schedule, intake, and course date information for the course "{global_last_discussed_course_name}" from the provided context.
            User Query: "{user_query}"
            Context from Website:
            {dynamic_context}
            
            Instructions:
            - Summarize all dates, times, and durations related to the course schedule.
            - If the information is not present, state: "The requested information is not available on the official website."
            - Do not include any extra sentences.
            - Always include the course URL at the end of the response.
            - Your final answer should be formatted as: "[Extracted Answer]\n\nFor more details, please refer to the official course website: [URL]"
            """
        else:
            # General prompt for other specific queries (fees, requirements)
            system_prompt = f"""
            You are a data extraction assistant. Find the exact piece of information requested by the user from the provided context for the course: "{global_last_discussed_course_name}".
            User Query: "{user_query}"
            Context from Website:
            {dynamic_context}
            
            Instructions:
            - Find the specific detail requested for the specified course.
            - Respond with a concise and direct answer. Do not include extra sentences.
            - If the information is not explicitly present, state: "The requested information is not available on the official website."
            - Always include the course URL at the end of the response.
            - Your final answer should be formatted as: "[Extracted Answer]\n\nFor more details, please refer to the official course website: [URL]"
            """
    else:
        # --- NEW & IMPROVED PROMPT for the initial query to provide structured, numbered list
        course_summaries = []
        # Separate full diplomas and modular certificates
        full_diplomas = []
        modular_courses = []

        for course_name in list(retrieved_course_names):
            if "modular" in course_name.lower() or "certificate" in course_name.lower():
                modular_courses.append(course_name)
            else:
                full_diplomas.append(course_name)

        # Prioritize full diplomas first, then add modular certificates
        courses_to_display = full_diplomas + modular_courses
        
        # Limit the display to a maximum of 3 courses
        for course_name in courses_to_display[:3]:
            details = dict_of_courses_structured.get(course_name, {})
            url = details.get('url', 'URL not available')
            description = details.get('description', 'Description not available.')
            course_code = details.get('course_code', 'N/A')

            course_summaries.append(
                f"**Course Name:** **{course_name}**\n"
                f"**Event Code:** {course_code}\n"
                f"**Description:** {description}\n"
                f"**URL:** {url}"
            )
        
        summaries_text = "\n\n".join(course_summaries)

        system_prompt = f"""
        You are a helpful AI assistant knowledgeable about BCA Academy's Specialist Diploma programmes.
        Your task is to provide a structured, numbered list of the top 3 most relevant courses based on the user's query.

        User Query: "{user_query}"

        Course Information Context (from multiple sources):
        {final_context}

        Instructions:
        1. Identify the top 3 most relevant courses from the provided context. When a query is about "project managers," consider courses on **Construction Management** and **BIM Management** as highly relevant. Prioritize full diploma programs over modular certificates.
        2. Format your response as a numbered list (e.g., "1. Course Name...").
        3. For each course, provide a concise summary using the following format:
           **Course Name:** [The full course name]
           **Event Code:** [The course event code]
           **Description:** [A brief summary of the course content]
           **URL:** [The official course URL]
        4. End the response with a final sentence directing the user to the table below for more details.
        
        Here are the course summaries to use:
        ---
        {summaries_text}
        ---
        """
        urls_str = "\n".join(retrieved_urls_with_names.values())
        system_prompt = f"{system_prompt}\n\nRelevant URLs:\n{urls_str}"
    
    messages = [{"role": "system", "content": system_prompt}]
    for role, content in conversation_history:
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_query})

    llm_response = get_llm_response(messages)

    conversation_history.append(("user", user_query))
    conversation_history.append(("assistant", llm_response))
    
    identified_course_from_retrieval = None
    if retrieved_course_names:
        identified_course_from_retrieval = next(iter(retrieved_course_names), None)

    # --- FIX: Ensure global_last_discussed_course_name is set correctly for initial queries ---
    if not has_specific_query and identified_course_from_retrieval:
        global_last_discussed_course_name = identified_course_from_retrieval
    
    course_details_list = []
    # --- FIX: Limit the table to show max 3 courses
    if retrieved_course_names:
        for course_name in list(retrieved_course_names)[:3]:
            if course_name in dict_of_courses_structured:
                course_details = dict_of_courses_structured[course_name].copy()
                course_url = course_details.get('url')
                if course_url:
                    print(f"Scraping details for table from {course_url}...")
                    scraped_content = fetch_url_content(course_url)

                    # --- NEW LOGIC: Extract the Event Code using a more specific regex
                    event_code_match = re.search(r'EVENT\s*CODE:\s*([A-Z0-9]+)', scraped_content, re.IGNORECASE)
                    if event_code_match:
                        course_details['course_code'] = event_code_match.group(1).strip()
                    else:
                        course_details['course_code'] = 'N/A'
                    
                    # --- NEW LOGIC: Use a mix of regex and LLM for robust table data extraction
                    # Extract fees using regex
                    fees_match = re.search(r'S\$[\d,]+\.[\d]{2}', scraped_content, re.IGNORECASE)
                    if fees_match:
                        course_details['price'] = fees_match.group(0)
                        
                    # Extract duration using regex
                    duration_match = re.search(r'(\d+\s+(?:month|year)s?)', scraped_content, re.IGNORECASE)
                    if duration_match:
                        course_details['duration'] = duration_match.group(0)

                    # Extract entry requirements using LLM
                    table_prompt_entry = f"""
                    You are a data extraction bot. Extract the entry requirements for the course "{course_name}" from the provided text.
                    Text:
                    {scraped_content}
                    Instructions:
                    - Respond only with the entry requirements as a single string.
                    - If the information is not present, use "N/A".
                    - Do not include any extra text or conversational filler.
                    """
                    response_entry = get_llm_response([{"role": "system", "content": table_prompt_entry}])
                    if "N/A" not in response_entry and "not available" not in response_entry:
                        course_details['entry_requirements'] = response_entry.strip()

                    # Extract schedule using LLM
                    table_prompt_schedule = f"""
                    You are a data extraction bot. Extract the schedule and intake dates for the course "{course_name}" from the provided text.
                    Text:
                    {scraped_content}
                    Instructions:
                    - Summarize the schedule and intake dates.
                    - If the information is not present, use "N/A".
                    - Do not include any extra text or conversational filler.
                    """
                    response_schedule = get_llm_response([{"role": "system", "content": table_prompt_schedule}])
                    if "N/A" not in response_schedule and "not available" not in response_schedule:
                        course_details['course_schedule'] = response_schedule.strip()

                course_details_list.append(course_details)
    
    # 🐛 DEBUGGING LINE: Print the list of course details
    print("--- Course Details List ---")
    print(course_details_list)
    print("---------------------------")
    
    return llm_response, course_details_list, has_specific_query

# --- 8. Initialize Data and FAISS Components on Module Import ---
load_structured_course_data()
load_faiss_components()