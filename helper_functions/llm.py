import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

# --- RECOMMENDED FIX START ---

# Ensure load_dotenv is called early.
# If .env is in the project root (where main.py is), and llm.py is in a subfolder,
# you need to tell load_dotenv where to find it by going up one directory.
# This makes it robust regardless of where llm.py is called from.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Check if OPENAI_API_KEY is available from .env
# If not, fall back to Streamlit secrets (for deployment)
# The variable name MUST be 'OPENAI_API_KEY' for the OpenAI client to pick it up automatically
# or when explicitly passed.
api_key = os.getenv('OPENAI_API_KEY')

if not api_key: # Check if it was loaded from .env
    # Fallback to Streamlit secrets if running on Streamlit Cloud or local secrets are used
    try:
        api_key = st.secrets['OPENAI_API_KEY']
        print("DEBUG: Loaded API key from Streamlit secrets.")
    except AttributeError:
        # Handle case where st.secrets is not configured or key is missing
        print("DEBUG: OPENAI_API_KEY not found in .env or Streamlit secrets.")
        # You might want to raise an error or handle this more gracefully
        # For now, we'll let the OpenAI client raise an error if key is None
        api_key = None # Ensure it's None if not found, to let OpenAI client fail clearly


# Pass the API Key to the OpenAI Client
# The client will raise AuthenticationError if api_key is None or incorrect
client = OpenAI(api_key=api_key)

# --- RECOMMENDED FIX END ---


def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]


# This is the "Updated" helper function for calling LLM
def get_completion(prompt, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output == True:
      output_json_structure = {"type": "json_object"}
    else:
      output_json_structure = None

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1,
        response_format=output_json_structure,
    )
    return response.choices[0].message.content


# Note that this function directly take in "messages" as the parameter.
def get_completion_by_messages(messages, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1
    )
    return response.choices[0].message.content


# This function is for calculating the tokens given the "message"
# ⚠️ This is simplified implementation that is good enough for a rough estimation
def count_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    return len(encoding.encode(text))


def count_tokens_from_message(messages):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))