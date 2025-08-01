import streamlit as st

def about_the_project_page():
    st.title("📘 About This Project")

    st.markdown("""
    ### Project Title: BCA Academy Specialist Diploma Course Advisory Assistant

    #### 👨‍💻 Team Members
    - Member 1: Kareemkhan Mahaboob Khan
    - Member 2: [Team Member Name]  # Fill in actual names here!
    - Member 3: [Team Member Name]  # Fill in actual names here!

    #### 🎯 Project Scope
    This web application provides contextualized course advisory based on user queries using a Large Language Model (LLM) and a robust **hybrid Retrieval-Augmented Generation (RAG)** system. It leverages both a **static FAISS vector store for general queries** and **real-time web scraping for specific, up-to-date information**.

    #### 🏗️ Objectives
    - To help users explore suitable Specialist Diploma courses at BCA Academy.
    - To offer tailored advice on admission requirements and course suitability.
    - To enhance decision-making through relevant course details and links.

    #### 📊 Data Sources
    - BCA Academy official course pages (e.g., [https://www.bcaa.edu.sg](https://www.bcaa.edu.sg))
    - Data collected and pre-processed into a structured JSON format.

    #### ⚙️ Features
    - **Hybrid RAG system:** Combines static knowledge with dynamic, real-time data.
    - **FAISS-powered semantic search** for highly relevant information retrieval.
    - **Real-time web scraping** for up-to-date details (e.g., fees, requirements).
    - Multi-course recommendation based on query.
    - Course metadata formatting: title, duration, admission, link.
    - Interactive and user-friendly Streamlit interface.

    #### 🧪 Technologies Used
    - **Python:** Core programming language.
    - **Streamlit:** For building the interactive web application interface.
    - **FAISS (Facebook AI Similarity Search):** Essential for efficient vector storage and rapid semantic similarity search.
    - **OpenAI API:** Utilized for both embedding generation (e.g., `text-embedding-ada-002`) and Large Language Model (e.g., GPT-3.5-turbo) inference.
    - **Requests:** For making HTTP requests to fetch web page content.
    - **Beautiful Soup 4 (bs4):** For parsing HTML and extracting structured data from web pages.
    - **LangChain (Components):** Used implicitly for powerful functionalities like text splitting and integration with embedding models.
    - **Python-Dotenv:** For secure management of environment variables (like API keys).
    - **Numpy:** For numerical operations, especially with embeddings.

    ---
    #### 📁 Project File Organization

    This Streamlit application is organized using a multi-page structure. For the application to function correctly, the files should be arranged as follows:

    ```
    .
    ├── main.py    # Main entry point of the app # Run as: streamlit run main.py
    │                           
    ├── build_faiss_index.py    # NOTE: Run this file before running the main app.
    ├── pages/
    │   ├── 01_About_the_project.py
    │   ├── 02_Methodology.py
    │   ├── 03_Chatbot.py
    │   ├── 04_How_to_use.py
    │   └── 05_View_All_Courses.py
    ├── data/
    │   ├── faiss_index.bin
    │   ├── faiss_metadata.json
    │   └── specialist_diploma_programmes.json
    ├── logs/
    │   └── user_interactions.jsonl
    ├── logics/
    │   └── customer_query_handler.py
    ├── helper_functions/
    │   ├── llm.py
    │   └── utility.py
    ├── .streamlit/
    │   └── secrets.toml
    ├── requirements.txt
    └── .env
    ```

    - **`main.py`**: This is the file you run with `streamlit run`. It serves as the home page and can contain general information or a welcome message.
    - **`build_faiss_index.py`**: This script is crucial for creating the vector store (`faiss_index.bin`) and its metadata. It must be run first.
    - **`pages/`**: This directory is where Streamlit automatically looks for additional pages to display in the sidebar menu. The numerical prefixes (e.g., `01_`) are used to control the display order.
    - **`data/`**: Stores input data file and the processed knowledge base files used by the RAG system.
    - **`logs/`**: Stores logs of user interactions for analysis.
    - **`logics/`**: Contains the core Python scripts that handle the application's business logic, such as the `ChatbotHandler` class.
    - **`helper_functions/`**: Contains reusable utility functions and LLM-related logic.
    - **`.streamlit/`**: A special directory for Streamlit configuration files, such as `secrets.toml` for securely managing API keys.
    - **`requirements.txt`**: Lists all the necessary Python libraries for the project to be installed via `pip`.
    - **`.env`**: Securely stores environment variables like your OpenAI API key.
    """)

if __name__ == "__main__":
    about_the_project_page()
