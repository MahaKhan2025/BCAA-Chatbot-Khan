import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="About Our Chatbot App" # More specific title
)
# endregion <--------- Streamlit App Configuration --------->

st.title("About the BCA Academy Chatbot")

st.write("This is a specialized Streamlit application designed to provide information about BCA Academy's Specialist Diploma programmes.")
st.write("It leverages a Large Language Model (LLM) to understand your queries and deliver relevant details from a curated knowledge base of course information.")

with st.expander("How to Use This Chatbot"):
    st.write("1. **Navigate to the 'Home' or 'Chat' page** (whichever your main chatbot interface is called).")
    st.write("2. **Type your question** about BCA Academy's Specialist Diploma programmes into the chat input box.")
    st.write("3. **Examples of what you can ask:**")
    st.write("   - 'Recommend courses for construction managers.'")
    st.write("   - 'Tell me about the Specialist Diploma in Integrated Project Management (SDIPM).' ")
    st.write("   - 'What are the fees for SDBCM?'")
    st.write("   - 'What are the entry requirements for the Construction Management diploma?'")
    st.write("   - 'When is the next intake for the Facility & Energy Management course?'")
    st.write("4. **Press Enter or click the send button** to submit your query.")
    st.write("5. The chatbot will process your request and provide a detailed answer based on the available course information.")

st.write("\n---")
st.markdown("Developed with ❤️ for BCA Academy's Specialist Diploma Programmes.")