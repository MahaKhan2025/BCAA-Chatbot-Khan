import json
import os
import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables (ensure OPENAI_API_KEY is in your .env file)
load_dotenv()

# --- Configuration ---
DATA_FILE_PATH = 'data/specialist_diploma_programmes.json'
FAISS_INDEX_PATH = 'data/faiss_index.bin' # Where to save the FAISS index
METADATA_PATH = 'data/faiss_metadata.json' # Where to save the chunk to course mapping

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL_NAME = "text-embedding-ada-002" # Or "text-embedding-3-small", "text-embedding-3-large"

# --- Function to load raw course data ---
def load_raw_course_data(json_file_path):
    """
    Loads raw course data from a JSON file, handling both list and dictionary root structures.
    It extracts 'title' as the course name and 'description' as the raw text for embeddings.
    """
    raw_data = {}
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list): # Confirmed: your JSON is a list of dictionaries
            print("Detected JSON as a list. Processing each item...")
            for item in data:
                if isinstance(item, dict):
                    course_title = item.get('title')
                    if course_title:
                        # Use the 'title' field as the main course name
                        # The 'raw_text' for embedding will come from the 'description' field
                        raw_data[course_title] = {
                            "raw_text": item.get('description', ''),
                            "url": item.get('url', ''),
                            "original_json_item": item # Storing the full item for metadata
                        }
                    else:
                        print(f"Warning: Item in JSON list missing 'title' key, skipping: {item}")
                else:
                    print(f"Warning: Skipping non-dictionary item in JSON list: {item}")
        elif isinstance(data, dict): # Fallback for a dictionary-based JSON (less likely given your data)
            print("Detected JSON as a dictionary. Processing key-value pairs...")
            for course_name, details in data.items():
                if isinstance(details, dict):
                     raw_data[course_name] = {
                        "raw_text": details.get('description', ''), # Assuming 'description' holds text
                        "url": details.get('url', ''),
                        "original_json_item": details
                    }
                else:
                    print(f"Warning: Skipping non-dictionary value for key '{course_name}' in JSON: {details}")
        else:
            print(f"Error: Unexpected JSON root type: {type(data)}. Expected a list or dictionary.")
            return {} # Return empty on unexpected structure

        print(f"Loaded raw data for {len(raw_data)} unique courses based on 'title'.")
        return raw_data
    except FileNotFoundError:
        print(f"Error: Course data file not found at {json_file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {json_file_path}. Check file format for validity. Error: {e}")
        return {}

# --- Main function to build and save the index ---
def build_and_save_faiss_index():
    print(f"--- Starting FAISS Index Building Process --- ({os.getcwd()})")

    # 1. Load Data
    dict_of_courses_raw = load_raw_course_data(DATA_FILE_PATH)
    if not dict_of_courses_raw:
        print("Exiting: No course data to process or data loading failed.")
        return

    # 2. Initialize Embedding Model
    print(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}...")
    try:
        embeddings_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
        print("Embedding model initialized.")
    except Exception as e:
        print(f"Error initializing embedding model: {e}. Check your OPENAI_API_KEY and network.")
        return

    # 3. Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    all_chunks = []
    chunk_to_course_map = [] # To store metadata for each chunk

    print("Splitting text into chunks and preparing metadata...")
    for course_name, course_info in dict_of_courses_raw.items():
        raw_text = course_info.get("raw_text", "")
        if raw_text:
            chunks = text_splitter.split_text(raw_text)
            for chunk in chunks:
                all_chunks.append(chunk)
                # Store chunk and original course name/info for retrieval
                chunk_to_course_map.append({
                    "chunk": chunk,
                    "original_course_name": course_name,
                    "url": course_info.get("url", ""),
                    "original_item_title": course_info["original_json_item"].get("title") # Get the title from the original item
                    # Add any other relevant metadata from course_info here if needed
                })
    print(f"Generated {len(all_chunks)} text chunks across {len(dict_of_courses_raw)} courses.")

    if not all_chunks:
        print("No text chunks generated. Check your data file and chunking logic.")
        return

    # 4. Generate Embeddings
    print(f"Generating embeddings for {len(all_chunks)} chunks (this might take time and cost tokens)...")
    try:
        chunk_embeddings = embeddings_model.embed_documents(all_chunks)
        chunk_embeddings_np = np.array(chunk_embeddings).astype('float32')
        print("Embeddings generated successfully.")
    except Exception as e:
        print(f"Error generating embeddings: {e}. Please check your OpenAI API key and network connection.")
        return

    # 5. Create and Add to FAISS Index
    print("Building FAISS index...")
    embedding_dimension = chunk_embeddings_np.shape[1]
    faiss_index = faiss.IndexFlatL2(embedding_dimension) # Using L2 (Euclidean distance)
    faiss_index.add(chunk_embeddings_np)
    print(f"FAISS index built with {faiss_index.ntotal} vectors.")

    # 6. Save FAISS Index and Metadata
    print(f"Saving FAISS index to {FAISS_INDEX_PATH} and metadata to {METADATA_PATH}...")
    try:
        # Ensure the 'data' directory exists
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)
        with open(METADATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(chunk_to_course_map, f, ensure_ascii=False, indent=2)
        print("FAISS index and metadata built and saved successfully!")
    except Exception as e:
        print(f"Error saving FAISS index or metadata: {e}")

if __name__ == "__main__":
    build_and_save_faiss_index()