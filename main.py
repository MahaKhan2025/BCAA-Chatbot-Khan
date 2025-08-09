# main.py
import sys
import os
import streamlit as st
import pandas as pd
import json

# Add the parent directory of this script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your functions
from logics.customer_query_handler import process_user_message
from helper_functions.utility import check_password, log_interaction

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="BCA Academy Course Chatbot"
)
# endregion <--------- Streamlit App Configuration --------->

st.title("📘 BCA Academy Specialist Diploma Chatbot")
st.markdown("""
Ask me anything about the Specialist Diploma Programmes offered by BCA Academy!
For example:
a) Suggest courses on construction management
b) Courses on BIM
c) Courses for civil engineers (or other professions)
You can also ask follow-up questions such as:
a) What are the course fees?
b) What are the entry requirements?
c) What is the course schedule?
""")
# Check if the password is correct.
# Place this at the very beginning to gate access
if not check_password():
    st.stop()

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "data_frame" in message and not message.get("is_follow_up"):
            st.dataframe(message["data_frame"])


# Accept user input
if prompt := st.chat_input("Ask about courses..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process user input
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Call your main processing function
            response_text, course_details_df_list, is_follow_up = process_user_message(prompt)

            # --- NEW: Log the interaction ---
            current_user = st.session_state.get("authenticated_user", "unknown_user")
            log_interaction(current_user, prompt, response_text)
            # --- END NEW LOGGING ---

            # Display assistant response
            st.markdown(response_text)

            # If course_details are returned AND it's not a follow-up query, display them as a DataFrame
            if course_details_df_list and not is_follow_up:
                df_to_display = pd.DataFrame(course_details_df_list)

                # Reorder columns as requested
                desired_column_order = [col for col in ['name', 'course_code', 'duration', 'price', 'entry_requirements', 'course_schedule', 'url'] if col in df_to_display.columns]
                df_to_display = df_to_display[desired_column_order]

                # Set index to start from 1
                df_to_display.index = range(1, len(df_to_display) + 1)

                st.markdown("**Course Details:**")
                st.dataframe(df_to_display)
                st.session_state.messages.append({"role": "assistant", "content": response_text, "data_frame": df_to_display, "is_follow_up": is_follow_up})
            else:
                st.session_state.messages.append({"role": "assistant", "content": response_text, "is_follow_up": is_follow_up})

# Optional: Add a clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    # Reset global context for the LLM
    from logics.customer_query_handler import global_last_discussed_course_name
    global_last_discussed_course_name = None
    st.rerun()