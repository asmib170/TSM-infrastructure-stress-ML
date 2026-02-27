# Importing Streamlit to build the dashboard UI
import streamlit as st

# Importing SQLite to read stored infrastructure data
import sqlite3

# Importing pandas for data manipulation
import pandas as pd

# Importing pickle to load the trained machine learning model
import pickle

# Importing os to check if the model file exists
import os

# Importing json to read saved model comparison metrics
import json

# Importing plotly for advanced visualizations
import plotly.express as px

# Setting dashboard configuration


# Setting the title and layout of the Streamlit page
st.set_page_config(page_title="TSM Stress Dashboard", layout="wide")

# Displaying the main title
st.title("TSM Infrastructure Stress Dashboard")



# Loading data from SQLite


# Defining the database path 
DB_NAME = os.path.join(os.path.dirname(__file__), "tsm_infrastructure.db")

# Creating a connection to the database
conn = sqlite3.connect(DB_NAME)

# Defining the SQL query to load the full dataset
query = "SELECT * FROM infrastructure_usage"

# Reading the table into a DataFrame
data = pd.read_sql(query, conn)

# Closing the database connection
conn.close()

# Stopping if no data exists
if data.empty:
    st.error("No data found in the database. Run `python data_generator.py` first.")
    st.stop()



# Loading the trained model 


# Defining the model file path
MODEL_PATH = os.path.join("models", "best_model.pkl")

# Stopping if the model file is missing
if not os.path.exists(MODEL_PATH):
    st.error("Model file not found. Run `python train_model.py` first to create models/best_model.pkl.")
    st.stop()

# Loading the model object
with open(MODEL_PATH, "rb") as file:
    loaded_obj = pickle.load(file)

# Initializing model variables
model = None
feature_columns = None
best_model_name = "Best Model"

# Handling NEW bundle format (dict with keys)
if isinstance(loaded_obj, dict) and "model" in loaded_obj:
    model = loaded_obj["model"]
    feature_columns = loaded_obj.get("feature_columns", None)
    best_model_name = loaded_obj.get("best_model_name", "Best Model")

# Handling OLD format (direct model object)
else:
    model = loaded_obj
    best_model_name = type(model).__name__



# Sidebar filters 


# Creating a sidebar title
st.sidebar.header("Filters (Analysis)")

# Creating a resource filter
resource_filter = st.sidebar.selectbox(
    "Resource Type",
    sorted(data["resource_type"].unique())
)

# Creating an exam phase filter
exam_filter = st.sidebar.selectbox(
    "Exam Phase",
    ["All"] + sorted(data["exam_phase"].unique())
)

# Building valid week choices based on selected exam phase
if exam_filter == "All":
    valid_weeks = sorted(data["week"].unique())
else:
    valid_weeks = sorted(data[data["exam_phase"] == exam_filter]["week"].unique())

# Creating a week selector that only allows valid weeks
week_filter = st.sidebar.selectbox(
    "Week",
    valid_weeks
)

# Filtering data based on selections
filtered = data[data["resource_type"] == resource_filter].copy()

if exam_filter != "All":
    filtered = filtered[filtered["exam_phase"] == exam_filter]

filtered_week = filtered[filtered["week"] == week_filter].copy()



# Showing deployed model name


# Displaying which model is deployed
st.caption(f"Deployed model: {best_model_name}")

# Displaying model comparison metrics if available
METRICS_PATH = os.path.join("models", "metrics.json")

if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH, "r") as f:
        metrics_payload = json.load(f)

    # Building performance table (RMSE, MAE, R2)
    perf = metrics_payload.get("metrics", {})
    rows = []

    for model_name, vals in perf.items():
        rows.append({
            "Model": model_name,
            "RMSE": vals.get("rmse", None),
            "MAE": vals.get("mae", None),
            "R2": vals.get("r2", None)
        })

    perf_df = pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)
    perf_df.insert(0, "Rank", range(1, len(perf_df) + 1))


    st.subheader("Model Comparison (RMSE / MAE / R²)")
    st.dataframe(perf_df, use_container_width=True, hide_index=True)

    # Model selection justification
    best_row = perf_df.iloc[0]
    best_name = str(best_row["Model"])
    best_rmse = float(best_row["RMSE"])

    st.subheader("Model Selection Justification")
    st.info(
        f"Selected Model: **{best_name}**\n\n"
        f"Reason: It achieved the lowest RMSE ({best_rmse:.4f}) among all candidate models, "
        f"while maintaining strong MAE and R² performance."
    )

    # Residual distribution
    residuals = metrics_payload.get("residuals", [])

    if isinstance(residuals, list) and len(residuals) > 0:
        st.subheader("Residual Error Distribution (Actual − Predicted)")

        res_df = pd.DataFrame({"Residual": residuals})

        fig = px.histogram(
            res_df,
            x="Residual",
            nbins=30,
            title="Residual Histogram (Actual − Predicted)"
        )

        fig.update_layout(height=450)

        st.plotly_chart(fig, use_container_width=True)



# Showing feature importance to explain model behavior
st.subheader("Top Feature Drivers (Explainability)")

# Initializing importance array
importances = None

# Extracting feature importances for CatBoost
if hasattr(model, "get_feature_importance"):
    try:
        importances = model.get_feature_importance()
    except:
        importances = None

# Extracting feature importances for tree-based sklearn models (RandomForest, etc.)
if importances is None and hasattr(model, "feature_importances_"):
    importances = model.feature_importances_

# Displaying feature importance if available:

if importances is not None and feature_columns is not None:
    # Creating a feature importance dataframe
    fi_df = pd.DataFrame({
        "Feature": feature_columns,
        "Importance": importances
    })

    # Sorting and taking top 15 drivers
    fi_df = fi_df.sort_values("Importance", ascending=False).head(15)

    # Creating interactive feature importance bar chart using Plotly
    fig = px.bar(
        fi_df,
        x="Feature",
        y="Importance",
        title="Top 15 Feature Importances"
    )

    # Rotating x-axis labels for readability
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="Features",
        yaxis_title="Importance Score",
        height=500
    )

    # Displaying the Plotly chart
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Feature importance is not available for the currently deployed model.")

# Showing top required KPIs 


# Creating 3 KPI cards
k1, k2, k3 = st.columns(3)

# Calculating KPI values
overall_avg = float(data["stress_score"].mean())
resource_avg = float(filtered["stress_score"].mean()) if not filtered.empty else 0.0

# Calculating week avg safely 
if filtered_week.empty:
    week_avg_display = "N/A"
else:
    week_avg_display = f"{float(filtered_week['stress_score'].mean()):.2f}"

# Displaying KPI cards
k1.metric("Overall Avg Stress", f"{overall_avg:.2f}")
k2.metric(f"{resource_filter} Avg Stress", f"{resource_avg:.2f}")
k3.metric(f"Week {week_filter} Avg Stress", week_avg_display)

# Warning if the filtered view has no rows
if filtered_week.empty:
    st.warning("No records found for this filter combination. Please adjust filters.")



# Section 1: Required Analysis


# Creating a clear section header
st.subheader("1) Analysis")

# Showing a small preview
st.write("Dataset Preview (first 20 rows):")
st.dataframe(data.head(20))

# Chart 1: Average stress by resource
st.write("Average Stress by Resource Type:")
avg_by_resource = data.groupby("resource_type")["stress_score"].mean().sort_values(ascending=False)
st.bar_chart(avg_by_resource)

# Chart 2: Stress trend across weeks for selected resource 
st.write(f"Stress Trend Across Weeks for {resource_filter}:")

trend_source = data[data["resource_type"] == resource_filter].copy()
if exam_filter != "All":
    trend_source = trend_source[trend_source["exam_phase"] == exam_filter]

trend = trend_source.groupby("week")["stress_score"].mean()
st.line_chart(trend)

# Table: Day × Time Slot stress (heatmap-style table) for selected week
st.write(f"Stress Table (Day of Week × Time Slot) for Week {week_filter}:")

if filtered_week.empty:
    st.info("No data available for this week and filter combination.")
else:
    # Creating pivot table
    pivot_df = filtered_week.pivot_table(
        index="day_of_week",
        columns="time_slot",
        values="stress_score",
        aggfunc="mean"
    ).fillna(0)

    # Defining correct chronological order for days and time slots
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    slot_order = ["Morning", "Afternoon", "Gap_8_9", "Peak_6_8", "Peak_9_12"]

    # Reordering rows and columns safely
    pivot_df = pivot_df.reindex(day_order)
    pivot_df = pivot_df.reindex(columns=slot_order)

    # Displaying ordered table
    st.dataframe(pivot_df)


# Section 2: Required Prediction (Demand -> Stress)


# Creating a clear section header
st.subheader("2) Prediction (Required)")

# Creating two columns for inputs
c1, c2 = st.columns(2)

# Defining prediction inputs
with c1:
    pred_resource = st.selectbox("Resource Type", sorted(data["resource_type"].unique()))
    pred_day = st.selectbox("Day of Week", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    pred_slot = st.selectbox("Time Slot", ["Morning", "Afternoon", "Gap_8_9", "Peak_6_8", "Peak_9_12"])

with c2:
    # Defining ordered exam phases
    phase_order = ["Regular", "UT1", "Mid-Term", "UT2", "End-Term"]

    # Creating exam week mapping for prediction
    exam_week_map = {
        "UT1": 3,
        "Mid-Term": 6,
        "UT2": 9,
        "End-Term": 12
    }

    # Selecting exam phase for prediction
    pred_phase = st.selectbox("Exam Phase", phase_order)

    # Auto-setting / restricting week based on exam phase
    if pred_phase in exam_week_map:
        pred_week = st.selectbox("Week", [exam_week_map[pred_phase]])
    else:
        regular_weeks = sorted(data[data["exam_phase"] == "Regular"]["week"].unique())
        pred_week = st.selectbox("Week", regular_weeks)

    pred_capacity = st.number_input("Effective Capacity", min_value=1, max_value=10, value=1)

# Showing quick helper for peak slot
is_peak = pred_slot in ["Peak_6_8", "Peak_9_12"]
st.info(f"Peak Slot: {'Yes' if is_peak else 'No'}")

# Creating the input DataFrame (no booking_requests input because the model predicts demand)
input_data = pd.DataFrame([{
    "effective_capacity": pred_capacity,
    "week": pred_week,
    "resource_type": pred_resource,
    "day_of_week": pred_day,
    "time_slot": pred_slot,
    "exam_phase": pred_phase
}])

# One-hot encoding the input like training
input_encoded = pd.get_dummies(input_data)

# Aligning columns with training columns 
if feature_columns is not None:
    input_encoded = input_encoded.reindex(columns=feature_columns, fill_value=0)

# Aligning columns with model feature names 
else:
    if hasattr(model, "feature_names_in_"):
        input_encoded = input_encoded.reindex(columns=model.feature_names_in_, fill_value=0)

# Predicting when button is clicked
if st.button("Predict"):

    # Predicting booking requests (demand)
    predicted_requests = float(model.predict(input_encoded)[0])

    # Preventing negative predictions
    predicted_requests = max(0.0, predicted_requests)

    # Calculating predicted stress using predicted demand and effective capacity
    predicted_stress = predicted_requests / pred_capacity

    # Displaying prediction outputs
    st.success(f"Predicted Booking Requests: {predicted_requests:.2f}")
    st.success(f"Predicted Stress Score: {predicted_stress:.2f}")

    # Giving a simple interpretation based on stress ratio
    if predicted_stress >= 3:
        st.warning("High Stress: predicted demand is multiple times the available capacity.")
    elif predicted_stress >= 1.5:
        st.info("Moderate Stress: predicted demand is higher than capacity. Monitor usage.")
    elif predicted_stress >= 1:
        st.info("Near Capacity: predicted demand is close to capacity.")
    else:
        st.success("Low Stress: predicted demand is comfortably within capacity.")