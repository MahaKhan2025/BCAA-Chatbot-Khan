# pages/04_About_the_project.py
import streamlit as st

def about_the_project_page():
    st.title("📘 About This Project")

    st.markdown("""
    ### Project Title: BCA Academy Specialist Diploma Course Advisory Assistant

    #### 👨‍💻 Team Members
    - Member 1: Kareemkhan Mahaboob Khan
    - Member 2: [Team Member Name]  # Not applicable
    - Member 3: [Team Member Name]  # Not applicable

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
    - **gspread:** Python API for Google Sheets to log user interactions.
    - **Google-Auth:** Library for authentication with Google services.

    ---
    #### 📁 Project File Organization

    This Streamlit application is organized using a multi-page structure. For the application to function correctly, the files should be arranged as follows:

    ```
    .
    ├── main.py     # Main entry point of the app
    ├── build_faiss_index.py
    ├── pages/
    │   ├── 01_main.py
    │   ├── 02_View_All_courses.py
    │   ├── 03_How_to_use.py
    │   ├── 04_About_the_project.py
    │   └── 05_Methodology.py
    ├── data/
    │   ├── faiss_index.bin
    │   ├── faiss_metadata.json
    │   └── specialist_diploma_programmes.json
    ├── logics/
    │   └── customer_query_handler.py
    ├── helper_functions/
    │   └── utility.py
    ├── .streamlit/
    │   └── secrets.toml  
    ├── requirements.txt
    └── .env
    ```
    """)

if __name__ == "__main__":
    about_the_project_page()