import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load Data ---
# We use pandas to read the study records from a CSV file
df = pd.read_csv('study_management.csv')

# Set the page title and a brief description of the application
st.title("Student Study Session Manager")
st.markdown("This application helps analyze study habits and session efficiency based on historical data.")

# --- Metrics Section ---
# Here we calculate some basic statistics to display at the top of the page
col1, col2, col3 = st.columns(3)
completion_rate = (df['Completion_Status'].mean() * 100)
avg_difficulty = df['Difficulty_Level'].mean()
total_hours = df['Actual_Hours_Spent'].sum()

# Display the calculated metrics in three separate columns
col1.metric("Completion Rate", f"{completion_rate:.1f}%")
col2.metric("Avg Difficulty", f"{avg_difficulty:.1f}/5")
col3.metric("Total Hours Studied", f"{total_hours} hrs")

# --- Visualization: Estimation Accuracy ---
# This section visualizes how accurate the study time estimates were compared to actual time spent
st.subheader("Study Time Estimation Accuracy")
# Calculate the difference between actual time and estimated time
df['Time_Variance'] = df['Actual_Hours_Spent'] - df['Estimated_Hours']
# Create a bar chart using Plotly Express
fig = px.bar(df, x='Subject', y='Time_Variance', color='Difficulty_Level',
             title="Time Variance by Subject (Actual vs Estimated)")
st.plotly_chart(fig)

# --- Task Logging Section ---
# Sidebar form to allow users to log new study sessions
st.sidebar.header("Log New Study Session")
with st.sidebar.form("study_form"):
    sub = st.selectbox("Select Subject", ["Math", "Physics", "Electronics", "Coding"])
    est = st.number_input("Estimated Hours", 1.0, 10.0, 2.0)
    act = st.number_input("Actual Hours Spent", 1.0, 10.0, 2.0)
    diff = st.slider("Difficulty Level (1-5)", 1, 5, 3)
    submitted = st.form_submit_button("Submit Log")
    
    if submitted:
        # Display a success message when the form is submitted
        st.success(f"Session for {sub} has been logged successfully.")