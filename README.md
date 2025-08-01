📚 BCA Academy Specialist Diploma Course Advisory AssistantThis project is a web-based course advisory assistant designed to help users find suitable Specialist Diploma courses at the BCA Academy. It utilizes a powerful hybrid Retrieval-Augmented Generation (RAG) system to provide accurate and up-to-date information.🌟 FeaturesHybrid RAG System: Combines a static knowledge base with real-time web scraping for dynamic data.FAISS Semantic Search: Uses a FAISS vector store for fast and relevant information retrieval based on user queries.Real-Time Data: Scrapes the BCA Academy website to ensure details like course fees and admission requirements are current.Tailored Recommendations: Offers multi-course recommendations and tailored advice based on specific query context.User-Friendly Interface: Built with Streamlit for a clean and interactive user experience.🛠️ Technologies UsedPython: The core programming language.Streamlit: For the web application's front-end interface.FAISS: Provides an efficient vector store for semantic search.OpenAI API: Used for generating embeddings and LLM inference.Beautiful Soup 4 (bs4): For parsing and extracting data from HTML.Requests: For making HTTP requests to fetch web page content.Python-Dotenv: For secure management of API keys and environment variables.Numpy: For numerical operations on vector embeddings.📁 Project StructureThe application is structured using a multi-page Streamlit layout..
├── your_main_app_file.py
├── build_faiss_index.py
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

🚀 Getting StartedPrerequisitesPython 3.8 or higher.A virtual environment is highly recommended.Local Setup & InstallationClone the repository from GitHub:git clone https://github.com/MahaKhan2025/BCAA-Chatbot-Khan.git

Navigate into the project directory:cd BCAA-Chatbot-Khan

Install the required dependencies using the requirements.txt file:pip install -r requirements.txt

Create your .env file with your OpenAI API key and your .streamlit/secrets.toml file with your secret information.How to RunMake sure your virtual environment is activated.Run the main Streamlit application from your terminal:streamlit run your_main_app_file.py

The app will open automatically in your web browser.Created by Kareemkhan Mahaboob Khan