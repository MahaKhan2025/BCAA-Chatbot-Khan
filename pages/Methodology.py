import streamlit as st
import streamlit.components.v1 as components # <-- NEW IMPORT FOR MERMAID HTML EMBEDDING

def methodology_page():
    st.title("🧠 Methodology & Architecture")

    st.markdown("""
    ### 🔄 Overview of System Architecture

    This application functions as a **Retrieval-Augmented Generation (RAG)** system, specifically designed to provide accurate and contextualized information about BCA Academy's Specialist Diploma programmes. When a user asks a question, the system first transforms the query into a numerical representation (embedding), uses **FAISS for efficient semantic search** to retrieve the most relevant information from its pre-indexed knowledge base, and then leverages a Large Language Model (LLM) to generate a precise and informative answer based on the retrieved context.

    ---
    ### 📁 Key Components

    - **FAISS Vector Store:** A highly optimized library for similarity search on dense vectors. During initialization, pre-processed course content is converted into embeddings (numerical vectors) and stored in a FAISS index, enabling rapid and scalable retrieval of semantically similar information based on user queries.
    - **In-Memory Structured Data Store:** Alongside the FAISS index, structured course details (like name, URL, etc.) are kept in Python dictionaries for direct access and to enrich the context provided to the LLM.
    - **OpenAI Embedding Model:** Transforms both user queries and the course content into high-dimensional numerical vectors, allowing for semantic comparison and retrieval using FAISS.
    - **Information Retrieval (FAISS-Powered):** Instead of simple keyword matching or full text scanning, user queries are embedded and then used to query the FAISS index. This retrieves the top 'k' most semantically relevant text chunks from the entire course knowledge base.
    - **Large Language Model (LLM) Response Generation:** An OpenAI GPT model receives the user's original query *augmented* with the semantically retrieved course information (from FAISS). This ensures the LLM generates a comprehensive, informative, and contextually accurate response.
    - **Conversation Context Management:** A mechanism tracks the "last discussed course" to handle subsequent, related questions without the user needing to explicitly repeat the course name, enabling a more natural conversational flow.

    ---
    """)

    # --- Use Case 1: Process Flow for Getting Replies from an Initial Query (Text Steps + Flowchart) ---

    st.markdown("""
    ### 🧭 Use Case 1: Process Flow for for Getting Replies from an Initial Query

    This describes how the chatbot handles a user's first query or a new, general question (e.g., "Recommend courses for project managers," or "What is the Specialist Diploma in Smart Facilities Management about?").

    1.  **User Inputs Query:** The user types their question into the chatbot interface.
    2.  **Query Embedding:** The user's input query is converted into a numerical vector (embedding) using the OpenAI Embedding Model.
    3.  **FAISS Retrieval:** This query embedding is used to perform a similarity search against the FAISS Vector Store, retrieving the most semantically relevant text chunks from all available course descriptions.
    4.  **Context Augmentation:** The retrieved text chunks, along with relevant structured course data, are combined with the user's original query to form a comprehensive prompt for the LLM.
    5.  **LLM Response Generation:** The LLM processes this augmented prompt and generates a comprehensive answer, which is then displayed to the user.
    6.  **Context Update:** If a specific course was discussed or recommended, its full name is stored as the 'last discussed course' to facilitate follow-up questions.
    """)

    # --- Start of HTML embed for Flowchart 1 ---
    mermaid_code_1 = """
    graph TD
        A[User Inputs Query] --> B[Generate Query Embedding];
        B --> C[FAISS Vector Store];
        C -- Top K relevant chunks --> D[Information Retrieval & Context Augmentation];
        D --> E{LLM Response Generation};
        E --> F[Display Response to User];
        E --> G[Update Conversation Context];
    """
    components.html(
        f"""
        <div class="mermaid">{mermaid_code_1}</div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
        </script>
        """,
        height=750, # <-- Height adjusted
    )
    # --- End of HTML embed for Flowchart 1 ---
    st.caption("Flowchart: Initial Query / Recommendation Process")


    st.markdown("""
    ---
    ### 🧭 Use Case 2: Process Flow for Follow-up Queries (Hybrid RAG)

    This describes how the chatbot handles questions that build on the previous turn, leveraging a combination of conversation context and real-time web scraping to get the most accurate details (e.g., "What are the fees?", "Entry requirements?").

    1.  **User Inputs Follow-up Query:** The user asks a specific question about the last discussed course (e.g., "What are the fees for that?") or explicitly mentions a course (e.g., "What about the schedule for SDCM?").
    2.  **Intent & Context Resolution:** The system analyzes the query for keywords like "fees" or "requirements" and, if found, uses the 'last discussed course' from the previous turn to resolve the full course name and retrieve its URL from the in-memory data store.
    3.  **Real-Time Web Scraping:** The system uses the retrieved course URL to dynamically fetch and scrape the content from the live course webpage. This is a critical step to get the most up-to-date information.
    4.  **Context Augmentation & Hybrid Context Creation:** The scraped webpage content is combined with the original FAISS-retrieved context and the conversation history to create a comprehensive, hybrid context.
    5.  **LLM Response Generation:** The LLM processes this enriched context and generates a precise answer for the specific query, drawing heavily from the live scraped data for accuracy.
    6.  **Display Response:** The generated answer is presented to the user, typically followed by a link to the official course website for further verification.
    """)

    # --- Start of HTML embed for Flowchart 2 (REVISED) ---
    mermaid_code_2 = """
    graph TD
        A[User Inputs Follow-up Query] --> B{Intent & Context Resolution};
        B -- Get URL from Course --> C[Real-Time Web Scraping];
        C --> D[Retrieve Webpage Content];
        D --> E[Combine with FAISS & Conversation Context];
        E --> F{LLM Response Generation};
        F --> G[Display Response to User];
    """
    components.html(
        f"""
        <div class="mermaid">{mermaid_code_2}</div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
        </script>
        """,
        height=1000, # <-- Adjusted height for this chart
    )
    # --- End of HTML embed for Flowchart 2 ---
    st.caption("Flowchart: Follow-up Query Process")

    # --- NEW SECTION: Interaction Logging Process ---
    st.markdown("""
    ---
    ### 🧭Use Case 3: Process Flow for Interaction Logging Process

    To facilitate monitoring, debugging, and future improvements, all user queries and the corresponding assistant responses are logged. This ensures a record of how users interact with the chatbot and the quality of generated replies.

    1.  **Interaction Trigger:** After the LLM generates a response to a user's query, the logging process is initiated.
    2.  **Retrieve User ID:** The authenticated user's ID (e.g., 'user1', 'user2') is retrieved from Streamlit's session state.
    3.  **Retrieve Log File Path:** The designated log file path (e.g., `logs/user_interactions.jsonl`) is obtained from the application's secrets configuration.
    4.  **Ensure Log Directory Exists:** The system checks if the directory for the log file exists and creates it if it doesn't.
    5.  **Prepare Log Entry:** A structured log entry is created, including a timestamp, the authenticated user's ID, the original query, and the assistant's final response.
    6.  **Append to Log File:** This structured entry (formatted as a JSON object) is appended as a new line to the specified log file, ensuring a continuous record of interactions.
    """)

    mermaid_code_3 = """
    graph TD
        A[User Submits Query] --> B{Assistant Generates Response};
        B --> C[Call log_interaction];
        C --> D[Get Authenticated User ID];
        D --> E[Get Log File Path];
        E --> F{Check/Create Log Directory};
        F --> G[Prepare Log Entry Details];
        G --> H[Append to Log File];
        H --> I[Interaction Logged];
    """
    components.html(
        f"""
        <div class="mermaid">{mermaid_code_3}</div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
        </script>
        """,
        height=1100, # Adjust height as needed for the logging flow
    )
    st.caption("Flowchart: Interaction Logging Process")
    # --- END NEW SECTION ---

    st.markdown("""
    ---
    ### 🔒 Security Measures
    - Password protection for app access (if implemented at Streamlit level).
    - Disclaimer included to warn about limitations of AI-generated content.
    - No personal or sensitive user data is collected or stored. All interactions are stateless beyond the immediate conversation context.

    ---
    ### 📝 Prompt Engineering
    Prompts are carefully constructed to guide the LLM's behavior, ensuring it performs specific tasks like intent recognition, information extraction, and generating user-friendly responses. This includes dynamically adding **FAISS-retrieved, semantically relevant course information** into the prompt's context to facilitate highly effective Retrieval-Augmented Generation.
    """)

if __name__ == "__main__":
    methodology_page()