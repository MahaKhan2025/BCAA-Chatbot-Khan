import streamlit as st
import hmac
import json
import os
import datetime 
import pytz 
import gspread # NEW: Google Sheets library
from oauth2client.service_account import ServiceAccountCredentials # NEW: For authentication

def check_password():
    """Returns `True` if the user had the correct username and password."""
    def password_entered_logic():
        """Checks whether a username and password entered by the user are correct."""
        if (
            st.session_state["submitted_username"] in st.secrets["allowed_users"] and
            hmac.compare_digest(st.session_state["submitted_password"], st.secrets["password"])
        ):
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = st.session_state["submitted_username"]
            del st.session_state["submitted_password"]
            del st.session_state["submitted_username"]
        else:
            st.session_state["password_correct"] = False
            del st.session_state["submitted_password"]
            del st.session_state["submitted_username"]

    if st.session_state.get("password_correct", False):
        return True

    with st.form("login_form"):
        username_input = st.text_input("Username", key="login_username_input")
        password_input = st.text_input("Password", type="password", key="login_password_input")
        
        submitted = st.form_submit_button("Login")

        if submitted:
            st.session_state["submitted_username"] = username_input
            st.session_state["submitted_password"] = password_input
            password_entered_logic()

    if "password_correct" in st.session_state:
        if not st.session_state["password_correct"]:
            st.error("😕 Invalid username or password")

    return False

def log_interaction(user_id: str, query: str, assistant_response: str):
    """
    Logs a user query and assistant response to a Google Sheet.
    """
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)

        spreadsheet = client.open('BCA Academy Chatbot Logs')
        worksheet = spreadsheet.sheet1
        
        # --- CHANGES ARE HERE ---
        # Get the current time in the 'Asia/Singapore' timezone
        singapore_tz = pytz.timezone('Asia/Singapore')
        timestamp = datetime.datetime.now(singapore_tz).strftime("%Y-%m-%d %H:%M:%S")

        log_entry = [
            timestamp, # Use the new timezone-aware timestamp
            user_id,
            query,
            assistant_response
        ]
        # --- END OF CHANGES ---

        worksheet.append_row(log_entry)
        
        print(f"Log captured for user '{user_id}' and saved to Google Sheets.")

    except Exception as e:
        print(f"Error logging interaction to Google Sheets: {e}")
        st.error(f"Error logging interaction: {e}")

def main_test_utility():
    if check_password():
        st.success(f"Welcome, {st.session_state.get('authenticated_user', 'User')}!")
        st.write("You are logged in.")
        if st.button("Log Test Interaction"):
            if 'authenticated_user' in st.session_state:
                log_interaction(st.session_state['authenticated_user'], "test query", "test response")
                st.write("Check your Google Sheet for the new entry.")
            else:
                st.warning("Please log in first to log a test interaction.")
    else:
        st.info("Please log in to access the application.")
        st.stop()

if __name__ == "__main__":
    if not hasattr(st, 'secrets'):
        try:
            with open(".streamlit/secrets.toml", "r") as f:
                import toml
                st.secrets = toml.load(f)
        except FileNotFoundError:
            st.secrets = {
                "password": "ai1234",
                "allowed_users": ["testuser"],
                "OPENAI_API_KEY": "sk-your-openai-api-key"
            }
    main_test_utility()