import streamlit as st
import hmac
import json
import os
import datetime # Import datetime for timestamps

def check_password():
    """Returns `True` if the user had the correct username and password."""

    # This function now doesn't need to be nested if we call it directly after form submission
    # We'll adapt it to directly use the values from st.session_state which are set by the form
    def password_entered_logic():
        """Checks whether a username and password entered by the user are correct."""
        if (
            st.session_state["submitted_username"] in st.secrets["allowed_users"] and
            hmac.compare_digest(st.session_state["submitted_password"], st.secrets["password"])
        ):
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = st.session_state["submitted_username"]
            # Clear the temporary submitted values
            del st.session_state["submitted_password"]
            del st.session_state["submitted_username"]
        else:
            st.session_state["password_correct"] = False
            # Clear the temporary submitted values on failure too
            del st.session_state["submitted_password"]
            del st.session_state["submitted_username"]


    # --- Authentication UI ---
    if st.session_state.get("password_correct", False):
        return True # Password was already correct from a previous run

    with st.form("login_form"):
        # We use local variables for the inputs within the form
        username_input = st.text_input("Username", key="login_username_input")
        password_input = st.text_input("Password", type="password", key="login_password_input")
        
        # The submit button
        submitted = st.form_submit_button("Login")

        # Only process authentication if the form was submitted
        if submitted:
            # Transfer current input values to session state keys that the logic uses
            st.session_state["submitted_username"] = username_input
            st.session_state["submitted_password"] = password_input
            password_entered_logic() # Call the logic function

    # Display error message if authentication failed on last attempt
    if "password_correct" in st.session_state:
        if not st.session_state["password_correct"]:
            st.error("😕 Invalid username or password")
            # Clear password_correct flag to allow retrying without re-running the app immediately
            # st.session_state["password_correct"] = False # This prevents immediate re-showing correct state

    return False

def log_interaction(user_id: str, query: str, assistant_response: str):
    """
    Logs a user query and assistant response to a JSON Lines file.

    Args:
        user_id (str): The ID of the authenticated user.
        query (str): The user's input query.
        assistant_response (str): The assistant's generated response.
    """
    log_file_path = st.secrets["interaction_log_file"]

    # Ensure the directory exists
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.datetime.now().isoformat() # ISO format for easy parsing

    log_entry = {
        "timestamp": timestamp,
        "user_id": user_id,
        "query": query,
        "assistant_response": assistant_response
    }

    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        # st.success("Interaction logged!") # Optional: For debugging, remove in production
    except Exception as e:
        st.error(f"Error logging interaction: {e}")

# Example of how you might use check_password (keep this for testing utility.py if desired)
def main_test_utility():
    if check_password():
        st.success(f"Welcome, {st.session_state.get('authenticated_user', 'User')}!")
        st.write("You are logged in.")
        # Example of logging
        if st.button("Log Test Interaction"):
            if 'authenticated_user' in st.session_state: # Ensure user is logged in for test
                log_interaction(st.session_state['authenticated_user'], "test query", "test response")
                st.write("Check your logs/user_interactions.jsonl file.")
            else:
                st.warning("Please log in first to log a test interaction.")
    else:
        st.info("Please log in to access the application.")
        st.stop()

if __name__ == "__main__":
    # Ensure st.secrets is available for testing this file directly
    if not hasattr(st, 'secrets'):
        try:
            with open(".streamlit/secrets.toml", "r") as f:
                import toml
                st.secrets = toml.load(f)
        except FileNotFoundError:
            st.secrets = {
                "password": "ai1234",
                "allowed_users": ["testuser"],
                "interaction_log_file": "logs/test_interactions.jsonl"
            }
    main_test_utility()