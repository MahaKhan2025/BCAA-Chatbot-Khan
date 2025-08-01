import streamlit as st
import pandas as pd
import json

st.title("List of Specialist Diploma training programmes offered by BCA Academy")

st.write("This list provides title of 15 programmes and their respective website urls and short description of each programme.")
# Load the JSON file
filepath = './data/specialist_diploma_programmes.json'
with open(filepath, 'r') as file:
    json_string = file.read()
    list_of_courses = json.loads(json_string)

# Create the DataFrame
df = pd.DataFrame(list_of_courses)

# Reorder the columns
desired_column_order = ['title', 'url', 'description']
df_reordered = df[desired_column_order]

# Set the index to start from 1
# This creates a new range for the index, starting at 1 and going up to the number of rows + 1
df_reordered.index = range(1, len(df_reordered) + 1)

# Display the reordered DataFrame with the new index in Streamlit
st.dataframe(df_reordered)