import streamlit as st
import json
import os
from openai import OpenAI
from collections import deque
import re
import faiss
import numpy as np
from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

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
    global dict_of_courses_structured
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            print("Structured course data is a list. Processing each item...")
            for item in data:
                course_title = item.get('title')
                if course_title:
                    dict_of_courses_structured[course_title] = {
                        'name': course_title,
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
    embeddings_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    print("Embedding model initialized.")

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

        return "\n".join(relevant_text)
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
        if re.search(r'\b' + re.escape(course_name) + r'\b', query, re.IGNORECASE):
            return course_name
    return None

# --- 7. Core Query Handling (Modified to use FAISS + Web Scraping) ---
def process_user_message(user_query: str):
    global global_last_discussed_course_name, conversation_history

    if faiss_index is None:
        load_faiss_components()
        if faiss_index is None:
            return "I'm sorry, my knowledge base could not be loaded. Please ensure all setup steps are complete.", []
    if embeddings_model is None:
        return "I'm sorry, the embedding model is not initialized.", []

    try:
        query_embedding = embeddings_model.embed_query(user_query)
        query_embedding_np = np.array([query_embedding]).astype('float32')
    except Exception as e:
        return f"Error embedding your query: {e}. Cannot perform search.", []

    k = 5
    distances, indices = faiss_index.search(query_embedding_np, k)

    retrieved_context = []
    retrieved_course_names = set()
    retrieved_urls = set()

    for i in indices[0]:
        if i != -1 and i < len(course_chunks_metadata):
            chunk_info = course_chunks_metadata[i]
            retrieved_context.append(chunk_info["chunk"])
            retrieved_course_names.add(chunk_info["original_item_title"])
            retrieved_urls.add(chunk_info["url"])

    context_str = "\n---\n".join(retrieved_context)

    dynamic_context = ""
    specific_detail_keywords = ["fee", "cost", "price", "charge", "entry", "requirements", "prerequisite", "schedule", "intake", "start date", "duration"]
    if any(keyword in user_query.lower() for keyword in specific_detail_keywords) and global_last_discussed_course_name:
        course_url = get_url_from_course_name(global_last_discussed_course_name)
        if course_url:
            print(f"User asked for details. Fetching content from {course_url}...")
            scraped_content = fetch_url_content(course_url)
            if scraped_content:
                dynamic_context = f"\n\n--- Dynamically Scraped Content from {course_url} ---\n{scraped_content}\n"
                print("Successfully scraped content. Adding to context.")
            else:
                print(f"Failed to scrape content from {course_url}. Relying on static context.")

    final_context = context_str + dynamic_context

    if not final_context:
        return "I couldn't find relevant information in my knowledge base. Please try rephrasing or ask about specific BCA Academy Specialist Diploma programmes.", []

    system_prompt_base = """
    You are a helpful AI assistant knowledgeable about BCA Academy's Specialist Diploma programmes.
    Your task is to provide detailed and helpful information based ONLY on the provided course context.

    The context may come from a static knowledge base or may be dynamically retrieved from a website. The dynamic content is often structured (e.g., in tables or lists). Prioritize information from the dynamically retrieved content if it is available and relevant to the user's query.

    When a user asks about a course, provide a comprehensive response that includes:
    1. A brief introduction of the course.
    2. A summary of the course content and objectives, including skills gained and career opportunities.
    3. A clear instruction to the user to 'For more details, please refer to the official course website:' followed by the course URL(s).

    When a user asks a follow-up question (e.g., about fees, entry requirements, or duration), use the context to provide the most accurate and up-to-date information available. If the information is not in the context, you must state that the information is not available and advise them to check the official course website for the most accurate and up-to-date details. You should always include the URL in the response.

    Your responses should be formatted clearly and professionally.
    """
    urls_str = "\n".join(retrieved_urls)
    system_prompt = f"{system_prompt_base}\n\nCourse Information Context:\n{final_context}\n\nRelevant URLs:\n{urls_str}"

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

    global_last_discussed_course_name = identified_course_from_retrieval
    
    course_details_list = []
    if retrieved_course_names:
        for course_name in retrieved_course_names:
            if course_name in dict_of_courses_structured:
                course_details_list.append(dict_of_courses_structured[course_name])

    return llm_response, course_details_list

# --- 8. Initialize Data and FAISS Components on Module Import ---
load_structured_course_data()
load_faiss_components()