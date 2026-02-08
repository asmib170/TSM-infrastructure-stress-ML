# Importing Streamlit to build the dashboard UI
import streamlit as st

# Importing SQLite to read stored infrastructure data
import sqlite3

# Importing pandas for data manipulation
import pandas as pd

# Importing pickle to load the trained machine learning model
import pickle



# Dashboard configuration

# Setting page title and layout
st.set_page_config(
    page_title="TSM Infrastructure Stress Dashboard",
    layout="wide"
)

# Displaying the dashboard title
st.title("TSM Infrastructure Stress Prediction Dashboard")



# Loading data from SQLite

# Defining the SQLite database file name
# Using an absolute path so the dashboard always reads the correct SQLite file
DB_NAME = r"C:\Users\batto\OneDrive\Desktop\TSM_infrastructure_stress_ML\tsm_infrastructure.db"


# Connecting to the SQLite database
conn = sqlite3.connect(DB_NAME)

# SQL query to fetch infrastructure usage data
query = "SELECT * FROM infrastructure_usage"

# Loading the data into a pandas DataFrame
data = pd.read_sql(query, conn)

# Closing the database connection
conn.close()



# Loading the trained model

# Loading the serialized best model
with open("models/best_model.pkl", "rb") as file:
    model = pickle.load(file)



# Data overview section

st.subheader("Infrastructure Usage Data (Preview)")

# Displaying a preview of the dataset
st.dataframe(data.head())



# Analytical visualization

st.subheader("Average Stress Score by Resource Type")

# Grouping data to compute average stress score per resource
avg_stress = data.groupby("resource_type")["stress_score"].mean().reset_index()

# Displaying bar chart
st.bar_chart(avg_stress.set_index("resource_type"))



# Prediction input section

st.subheader("Predict Infrastructure Stress")

# User input fields
resource_type = st.selectbox(
    "Select Resource Type",
    data["resource_type"].unique()
)

day_of_week = st.selectbox(
    "Select Day of Week",
    data["day_of_week"].unique()
)

time_slot = st.selectbox(
    "Select Time Slot",
    data["time_slot"].unique()
)

exam_phase = st.selectbox(
    "Select Exam Phase",
    data["exam_phase"].unique()
)

week = st.slider(
    "Select Academic Week",
    min_value=1,
    max_value=12,
    value=6
)

effective_capacity = st.number_input(
    "Effective Capacity",
    min_value=1,
    max_value=5,
    value=1
)

booking_requests = st.number_input(
    "Expected Booking Requests",
    min_value=0,
    max_value=20,
    value=5
)



# Preparing input for prediction

# Creating a DataFrame from user input
input_data = pd.DataFrame([{
    "effective_capacity": effective_capacity,
    "week": week,
    "booking_requests": booking_requests,
    "resource_type": resource_type,
    "day_of_week": day_of_week,
    "time_slot": time_slot,
    "exam_phase": exam_phase
}])

# Applying one-hot encoding
input_encoded = pd.get_dummies(input_data)

# Aligning input columns with training features
input_encoded = input_encoded.reindex(
    columns=model.feature_names_in_,
    fill_value=0
)



# Making prediction

if st.button("Predict Stress Level"):

    # Predicting stress score
    prediction = model.predict(input_encoded)[0]

    # Displaying prediction result
    st.success(f"Predicted Infrastructure Stress Score: {round(prediction, 2)}")
