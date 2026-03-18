# Importing Streamlit to build the interactive dashboard interface.
import streamlit as st

# Importing SQLite so the dashboard can read stored infrastructure usage data from the local database.
import sqlite3

# Importing pandas for loading, filtering, transforming, and aggregating tabular data.
import pandas as pd

# Importing pickle to load the trained machine learning model saved on disk.
import pickle

# Importing os for file-path construction and file existence checks.
import os

# Importing json to read the saved model metrics JSON file.
import json

# Importing math so I can convert exact model outputs into a more human-friendly demand range.
import math

# Importing Plotly Express to create clean interactive charts.
import plotly.express as px

# Setting the Streamlit page configuration before any UI is rendered.
# Important syntax: layout="wide" tells Streamlit to use a wider page layout.
st.set_page_config(
    page_title="TSM Infrastructure Capacity Dashboard",
    page_icon="🎵",
    layout="wide",
)

# Injecting custom CSS to give the dashboard a premium startup-style look and to use more screen width.
# Important syntax: st.markdown(..., unsafe_allow_html=True) allows raw HTML and CSS rendering.
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(44, 84, 160, 0.18), transparent 30%),
            radial-gradient(circle at top right, rgba(0, 180, 216, 0.12), transparent 28%),
            linear-gradient(180deg, #07101d 0%, #091423 40%, #0b1728 100%);
        color: #f5f7fb;
    }

    .block-container {
        max-width: 96vw !important;
        padding-top: 1.15rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
        padding-bottom: 1.2rem;
    }

    .hero-wrap {
        background: linear-gradient(135deg, rgba(17, 28, 47, 0.92), rgba(12, 20, 35, 0.88));
        border: 1px solid rgba(140, 166, 201, 0.15);
        border-radius: 26px;
        padding: 1.35rem 1.45rem 1.15rem 1.45rem;
        box-shadow: 0 22px 50px rgba(0, 0, 0, 0.28);
        margin-bottom: 1rem;
    }

    .hero-chip {
        display: inline-block;
        padding: 0.34rem 0.82rem;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        background: rgba(0, 180, 216, 0.12);
        color: #8ee9ff;
        border: 1px solid rgba(0, 180, 216, 0.24);
        margin-bottom: 0.7rem;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin-bottom: 0.34rem;
    }

    .hero-subtitle {
        font-size: 1.14rem;
        color: #afbdd3;
        margin-bottom: 0.1rem;
        max-width: 980px;
        line-height: 1.55;
    }

    .section-title {
        font-size: 1.34rem;
        font-weight: 800;
        color: #eef4ff;
        margin-top: 0.25rem;
        margin-bottom: 0.78rem;
    }

    .glass-card {
        background: linear-gradient(180deg, rgba(13, 23, 39, 0.96), rgba(16, 28, 46, 0.94));
        border: 1px solid rgba(139, 163, 196, 0.14);
        border-radius: 22px;
        padding: 1rem 1rem 0.95rem 1rem;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
    }

    .mini-label {
        font-size: 0.98rem;
        font-weight: 700;
        color: #9eb2cf;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.28rem;
    }

    .big-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }

    .helper-text {
        font-size: 1.08rem;
        color: #9fb0c7;
        line-height: 1.6;
    }

    .alert-card {
        background: linear-gradient(90deg, rgba(255, 112, 67, 0.14), rgba(255, 193, 7, 0.08));
        border: 1px solid rgba(255, 164, 120, 0.18);
        border-radius: 18px;
        padding: 1rem 1.08rem;
        margin-bottom: 1rem;
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.18);
    }

    .alert-title {
        font-size: 0.94rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #ffd2b8;
        margin-bottom: 0.24rem;
    }

    .alert-text {
        font-size: 1.12rem;
        color: #fff1e8;
        line-height: 1.6;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(13, 23, 39, 0.96), rgba(16, 28, 46, 0.94));
        border: 1px solid rgba(139, 163, 196, 0.14);
        border-radius: 22px;
        padding: 0.95rem 1rem 0.8rem 1rem;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
        min-height: 130px;
    }

    div[data-testid="stMetricLabel"] {
        color: #b8c7df;
        font-size: 1.08rem;
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 1.45rem;
        font-weight: 700;
        line-height: 1.2;
    }

    .status-pill {
        display: inline-block;
        padding: 0.42rem 0.78rem;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-top: 0.4rem;
        margin-bottom: 0.35rem;
    }

    .pill-underused {
        background: rgba(46, 204, 113, 0.14);
        color: #8cf1b5;
        border: 1px solid rgba(46, 204, 113, 0.28);
    }

    .pill-healthy {
        background: rgba(0, 180, 216, 0.15);
        color: #9cecff;
        border: 1px solid rgba(0, 180, 216, 0.28);
    }

    .pill-watch {
        background: rgba(255, 193, 7, 0.15);
        color: #ffe08a;
        border: 1px solid rgba(255, 193, 7, 0.28);
    }

    .pill-overloaded {
        background: rgba(239, 83, 80, 0.16);
        color: #ffadad;
        border: 1px solid rgba(239, 83, 80, 0.28);
    }

    .result-box {
        background: linear-gradient(180deg, rgba(15, 27, 45, 0.95), rgba(11, 21, 37, 0.96));
        border: 1px solid rgba(139, 163, 196, 0.14);
        border-radius: 20px;
        padding: 1rem;
        margin-top: 0.95rem;
    }

    .streamlit-expanderHeader {
        font-weight: 800;
        color: #eef4ff;
        font-size: 1.12rem;
    }

    .stCaption {
        font-size: 1.08rem !important;
        color: #aebed6 !important;
        line-height: 1.55 !important;
    }

    label, .stSelectbox label, .stNumberInput label {
        font-size: 1.08rem !important;
        font-weight: 700 !important;
        color: #eef4ff !important;
    }

    .tech-note {
        font-size: 1.06rem;
        color: #d7e3f5;
        line-height: 1.6;
        margin-bottom: 0.8rem;
    }

    .tech-subtitle {
        font-size: 1.1rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.55rem;
    }

    .guide-box {
        background: linear-gradient(180deg, rgba(15, 27, 45, 0.95), rgba(11, 21, 37, 0.96));
        border: 1px solid rgba(139, 163, 196, 0.14);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-top: 0.85rem;
    }

    .guide-title {
        font-size: 1.02rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.28rem;
    }

    .guide-text {
        font-size: 1.02rem;
        color: #c8d5e8;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Defining the base directory so all project file paths work relative to this script.
# Important syntax: os.path.dirname(__file__) returns the folder where the current file exists.
BASE_DIR = os.path.dirname(__file__)

# Defining the database path for the SQLite file.
DB_PATH = os.path.join(BASE_DIR, "tsm_infrastructure.db")

# Defining the trained best-model pickle path.
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_model.pkl")

# Defining the metrics JSON file path.
METRICS_PATH = os.path.join(BASE_DIR, "models", "metrics.json")

# Creating a helper function to load the infrastructure dataset from SQLite into a pandas DataFrame.
def load_data() -> pd.DataFrame:
    # Opening a connection to the SQLite database file.
    conn = sqlite3.connect(DB_PATH)

    # Reading the full infrastructure_usage table into a DataFrame.
    # Important syntax: pd.read_sql(...) runs the SQL query and returns a pandas DataFrame.
    df = pd.read_sql("SELECT * FROM infrastructure_usage", conn)

    # Closing the database connection after reading the data.
    conn.close()

    # Returning the loaded DataFrame.
    return df

# Creating a helper function to load the saved model bundle and its metadata.
def load_model_bundle():
    # Opening the pickle file in binary read mode because pickle stores byte data.
    with open(MODEL_PATH, "rb") as file:
        # Loading the saved Python object from the pickle file.
        loaded_obj = pickle.load(file)

    # Checking whether the saved object is a dictionary bundle containing model metadata.
    if isinstance(loaded_obj, dict) and "model" in loaded_obj:
        # Extracting the trained model object.
        model = loaded_obj["model"]

        # Extracting the saved feature column order.
        feature_columns = loaded_obj.get("feature_columns", None)

        # Extracting the saved best model name for display.
        best_model_name = loaded_obj.get("best_model_name", "Best Model")
    else:
        # Falling back to older save format where the file contains only the model itself.
        model = loaded_obj

        # Setting feature columns to None because older save format may not include them.
        feature_columns = None

        # Using the Python class name as a fallback display model name.
        best_model_name = type(model).__name__

    # Returning the loaded model, feature columns, and model name.
    return model, feature_columns, best_model_name

# Creating a helper function to load the metrics JSON payload if the file exists.
def load_metrics_payload() -> dict:
    # Checking if the metrics file exists before opening it.
    if os.path.exists(METRICS_PATH):
        # Opening the metrics JSON file.
        with open(METRICS_PATH, "r") as file:
            # Parsing and returning the JSON data as a Python dictionary.
            return json.load(file)

    # Returning an empty dictionary if the metrics file does not exist.
    return {}

# Creating a helper function to convert stored time-slot codes into human-friendly labels.
def format_slot_name(slot_value: str) -> str:
    # Defining a mapping from internal slot names to cleaner display labels.
    slot_map = {
        "Peak_9_12": "Peak 9 PM–12 AM",
        "Peak_6_8": "Peak 6–8 PM",
        "Gap_8_9": "Gap 8–9 PM",
        "Morning": "Morning",
        "Afternoon": "Afternoon",
    }

    # Returning the mapped display value if found, otherwise replacing underscores with spaces.
    return slot_map.get(slot_value, str(slot_value).replace("_", " "))

# Creating a helper function to convert the pressure score into a human-readable category.
# Important logic: these product-facing thresholds are intentionally tuned so the system
# feels operationally meaningful and not falsely "underused" at moderate load levels.
def pressure_band_label(pressure_value: float) -> str:
    # Returning Underused only when pressure is clearly low.
    if pressure_value < 0.50:
        return "Underused"

    # Returning Healthy for moderate but comfortable load.
    if pressure_value < 0.80:
        return "Healthy"

    # Returning Near Capacity for the range where the system feels meaningfully utilized
    # and potentially tighter from an operations perspective.
    if pressure_value < 1.60:
        return "Near Capacity"

    # Returning Overloaded when demand clearly pushes beyond comfortable capacity.
    return "Overloaded"

# Creating a helper function to render a colored pressure pill in HTML.
def render_status_pill(pressure_value: float) -> str:
    # Returning a green pill for clearly low-pressure situations.
    if pressure_value < 0.50:
        return '<span class="status-pill pill-underused">Underused</span>'

    # Returning a blue pill for comfortable but active usage.
    if pressure_value < 0.80:
        return '<span class="status-pill pill-healthy">Healthy</span>'

    # Returning a yellow pill when the system is getting tight.
    if pressure_value < 1.60:
        return '<span class="status-pill pill-watch">Near Capacity</span>'

    # Returning a red pill for overloaded situations.
    return '<span class="status-pill pill-overloaded">Overloaded</span>'

# Creating a helper function to convert the model's exact decimal prediction into a rounded booking range.
def format_demand_range(predicted_value: float) -> str:
    # Rounding down to the nearest whole booking request.
    lower_bound = math.floor(predicted_value)

    # Rounding up to the nearest whole booking request.
    upper_bound = math.ceil(predicted_value)

    # Returning a simple single-number format if both bounds are the same.
    if lower_bound == upper_bound:
        return f"~{lower_bound} bookings"

    # Returning a clearer range format if the decimal prediction falls between two integers.
    return f"~{lower_bound} to {upper_bound} bookings"

# Checking whether the database file exists before proceeding.
if not os.path.exists(DB_PATH):
    # Showing an error if the database has not been generated yet.
    st.error("Database not found. Run `python data_generator.py` first.")

    # Stopping app execution because later steps depend on the database.
    st.stop()

# Checking whether the saved best-model file exists before loading it.
if not os.path.exists(MODEL_PATH):
    # Showing an error if the model has not been trained and saved yet.
    st.error("Best model not found. Run `python train_model.py` first.")

    # Stopping app execution because prediction depends on the model.
    st.stop()

# Loading the infrastructure dataset from the database.
data = load_data()

# Checking whether the dataset is empty.
if data.empty:
    # Showing an error if the table exists but contains no rows.
    st.error("No data found in the database. Run `python data_generator.py` first.")

    # Stopping app execution because the dashboard cannot render without data.
    st.stop()

# Loading the trained model bundle and metadata.
model, feature_columns, best_model_name = load_model_bundle()

# Loading the saved metrics payload for technical display.
metrics_payload = load_metrics_payload()

# Rendering the hero header section at the top of the dashboard.
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-chip">Operational Decision Dashboard</div>
        <div class="hero-title">TSM Infrastructure Capacity Dashboard</div>
        <div class="hero-subtitle">
            Spot pressure early. Adjust capacity before bottlenecks build.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Calculating the total observed booking demand across the whole dataset.
# Important logic: sum() adds the booking_requests values, so this is total demand observed, not number of rows.
total_demand = float(data["booking_requests"].sum())

# Calculating the average pressure score across the whole dataset.
# Important logic: this is the mean of demand / capacity, not a raw count.
avg_pressure = float(data["stress_score"].mean())

# Converting the average pressure score into a readable business label.
avg_pressure_label = pressure_band_label(avg_pressure)

# Grouping data by resource type to compute average pressure per resource.
stress_by_resource = (
    data.groupby("resource_type", as_index=False)["stress_score"]
    .mean()
    .sort_values("stress_score", ascending=False)
)

# Grouping data by time slot to compute average pressure per slot.
stress_by_slot = (
    data.groupby("time_slot", as_index=False)["stress_score"]
    .mean()
    .sort_values("stress_score", ascending=False)
)

# Defining the logical order of academic exam phases.
exam_phase_order = ["Regular", "UT1", "Mid-Term", "UT2", "End-Term"]

# Grouping data by exam phase to calculate average pressure in each phase.
stress_by_phase = data.groupby("exam_phase", as_index=False)["stress_score"].mean()

# Converting exam_phase into an ordered categorical type so the phases display in academic order.
stress_by_phase["exam_phase"] = pd.Categorical(
    stress_by_phase["exam_phase"],
    categories=exam_phase_order,
    ordered=True,
)

# Sorting exam phases using the custom academic order.
stress_by_phase = stress_by_phase.sort_values("exam_phase")

# Extracting the highest-pressure resource from the resource summary.
top_pressure_resource = str(stress_by_resource.iloc[0]["resource_type"])

# Extracting the highest-pressure time slot and formatting it for display.
peak_pressure_slot_raw = str(stress_by_slot.iloc[0]["time_slot"])
peak_pressure_window = format_slot_name(peak_pressure_slot_raw)

# Extracting the exam phase with the highest seasonal pressure.
highest_phase = str(stress_by_phase.sort_values("stress_score", ascending=False).iloc[0]["exam_phase"])

# Rendering a priority alert card below the hero section for immediate decision support.
st.markdown(
    f"""
    <div class="alert-card">
        <div class="alert-title">Priority Alert</div>
        <div class="alert-text">
            <b>{top_pressure_resource}</b> is currently under the highest pressure, with the greatest risk during
            <b>{peak_pressure_window}</b>. Exam-period demand is strongest in <b>{highest_phase}</b>.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Creating four KPI cards across the screen for an instant operational summary.
kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="large")

# Rendering the total demand observed KPI.
with kpi1:
    # Showing the total demand observed across the dashboard data.
    # Important syntax: help=... adds a tooltip to the metric label.
    st.metric(
        "Total Demand Observed",
        f"{total_demand:,.0f}",
        help="Total number of booking requests recorded across the current dashboard data. This reflects observed demand, not capacity.",
    )

    # Adding helper text under the KPI so the number has context.
    st.caption("Total booking requests recorded across the current dashboard data.")

# Rendering the average capacity pressure KPI.
with kpi2:
    # Showing the average pressure score together with its business meaning.
    st.metric(
        "Average Capacity Pressure",
        f"{avg_pressure:.2f} · {avg_pressure_label}",
        help=(
            "Capacity Pressure = booking requests ÷ effective capacity.\n\n"
            "Below 0.5 = Underused\n"
            "0.5 to 0.8 = Healthy\n"
            "0.8 to 1.6 = Near Capacity\n"
            "Above 1.6 = Overloaded"
        ),
    )

    # Adding helper text under the KPI so the number has context.
    st.caption("Pressure is calculated as demand divided by available capacity.")

# Rendering the top pressure resource KPI.
with kpi3:
    # Showing which resource is under the most pressure on average.
    st.metric(
        "Top Pressure Resource",
        top_pressure_resource,
        help="Resource experiencing the highest average demand relative to its available capacity.",
    )

    # Adding helper text under the KPI.
    st.caption("Resource with the highest average pressure across the data.")

# Rendering the peak pressure window KPI.
with kpi4:
    # Showing the time slot with the strongest average pressure.
    st.metric(
        "Peak Pressure Window",
        peak_pressure_window,
        help="Time slot where demand places the greatest pressure on available capacity.",
    )

    # Adding helper text under the KPI.
    st.caption("Time slot with the highest average pressure.")

# Creating the main dashboard layout with a wider analytics area and a narrower right-side planning panel.
main_left, main_right = st.columns([2.3, 1], gap="large")

# Building the left side where the main analytics will be displayed.
with main_left:
    # Rendering a section heading for the analytics area.
    st.markdown('<div class="section-title">Where should TSM act first?</div>', unsafe_allow_html=True)

    # Adding a short explanatory caption before the first chart.
    st.caption("Higher values indicate stronger demand pressure relative to available capacity.")

    # Creating the main bar chart that shows which resources need attention first.
    fig_resource = px.bar(
        stress_by_resource,
        x="resource_type",
        y="stress_score",
        title="Which Resources Need Attention?",
        text_auto=".2f",
    )

    # Styling the resource chart to match the dashboard theme.
    fig_resource.update_layout(
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,23,39,0.96)",
        font_color="#eef4ff",
        margin=dict(l=18, r=18, t=60, b=18),
        xaxis_title="Resource Type",
        yaxis_title="Average Capacity Pressure",
        title_font=dict(size=22),
        xaxis=dict(title_font=dict(size=16), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=16), tickfont=dict(size=14)),
    )

    # Displaying the resource chart.
    st.plotly_chart(fig_resource, use_container_width=True)

    # Creating two side-by-side lower charts to keep the dashboard compact and one-screen.
    lower_left, lower_right = st.columns(2, gap="large")

    # Building the lower-left chart for time-slot pressure.
    with lower_left:
        # Creating a clean copy of slot data for display label transformation.
        slot_chart_df = stress_by_slot.copy()

        # Converting internal slot names to office-friendly labels.
        slot_chart_df["display_slot"] = slot_chart_df["time_slot"].apply(format_slot_name)

        # Adding a small caption so the chart is easier to interpret.
        st.caption("Shows which time windows place the most pressure on available capacity.")

        # Creating the bar chart showing when demand peaks.
        fig_slot = px.bar(
            slot_chart_df,
            x="display_slot",
            y="stress_score",
            title="When Does Demand Peak?",
            text_auto=".2f",
        )

        # Styling the slot chart for consistency with the dashboard design.
        fig_slot.update_layout(
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,23,39,0.96)",
            font_color="#eef4ff",
            margin=dict(l=18, r=18, t=60, b=18),
            xaxis_title="Time Slot",
            yaxis_title="Average Capacity Pressure",
            title_font=dict(size=22),
            xaxis=dict(title_font=dict(size=16), tickfont=dict(size=14)),
            yaxis=dict(title_font=dict(size=16), tickfont=dict(size=14)),
        )

        # Rotating x-axis labels slightly to improve readability.
        fig_slot.update_xaxes(tickangle=-18)

        # Displaying the time-slot chart.
        st.plotly_chart(fig_slot, use_container_width=True)

    # Building the lower-right chart for exam-phase pressure.
    with lower_right:
        # Adding a small caption so the chart is easier to interpret.
        st.caption("Compares how demand pressure shifts across regular weeks and exam phases.")

        # Creating a line chart to show how demand changes across academic phases.
        fig_phase = px.line(
            stress_by_phase,
            x="exam_phase",
            y="stress_score",
            title="How Do Exam Periods Change Demand?",
            markers=True,
        )

        # Styling the exam-phase chart for the dark dashboard theme.
        fig_phase.update_layout(
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,23,39,0.96)",
            font_color="#eef4ff",
            margin=dict(l=18, r=18, t=60, b=18),
            xaxis_title="Exam Phase",
            yaxis_title="Average Capacity Pressure",
            title_font=dict(size=22),
            xaxis=dict(title_font=dict(size=16), tickfont=dict(size=14)),
            yaxis=dict(title_font=dict(size=16), tickfont=dict(size=14)),
        )

        # Displaying the exam-phase chart.
        st.plotly_chart(fig_phase, use_container_width=True)

    # Rendering a key insight card that summarizes the main story in words.
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="mini-label">Key Insight</div>
            <div class="big-value" style="font-size:1.45rem;">{top_pressure_resource} should be reviewed first</div>
            <div class="helper-text">
                {top_pressure_resource} shows the highest sustained pressure across the dashboard.
                Demand is strongest during <b>{peak_pressure_window}</b>, while <b>{highest_phase}</b> shows the sharpest seasonal increase.
                This suggests that {top_pressure_resource} scheduling, access rules, or usable capacity should be reviewed first.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Building the right-side panel for capacity planning and scenario simulation.
with main_right:
    # Opening a styled glass-card container for the prediction panel.
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    # Rendering the title for the right-side simulation section.
    st.markdown('<div class="section-title">Capacity Planning Simulator</div>', unsafe_allow_html=True)

    # Showing a tighter and cleaner explanation of what powers the simulator.
    st.caption(f"Estimates demand for the selected scenario using the deployed {best_model_name} model.")

    # Creating a mapping of default capacities for each resource so users are not forced to guess the number.
    # Important logic: these defaults are kept aligned with the updated synthetic data generator.
    resource_capacity_map = {
        "Live_Room": 10,
        "Studio": 12,
        "MP_Lab": 8,
        "MPR_Basic": 6,
        "MPR_Equipped": 6,
        "MPR_Moldy": 5,
    }

    # Creating the resource dropdown so the user can select the infrastructure type.
    pred_resource = st.selectbox(
        "Resource Type",
        sorted(data["resource_type"].unique()),
        help="Select the type of space or facility you want to evaluate.",
    )

    # Creating the day-of-week dropdown.
    pred_day = st.selectbox(
        "Day of Week",
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        help="Choose the day for which you want to estimate expected demand.",
    )

    # Creating the time-slot dropdown with cleaned display labels.
    pred_slot = st.selectbox(
        "Time Slot",
        ["Morning", "Afternoon", "Gap_8_9", "Peak_6_8", "Peak_9_12"],
        format_func=format_slot_name,
        help="Select the usage window being evaluated.",
    )

    # Creating the exam-phase dropdown.
    pred_phase = st.selectbox(
        "Exam Phase",
        exam_phase_order,
        help="Academic period can significantly change booking demand.",
    )

    # Defining realistic week mappings for exam phases.
    exam_week_map = {
        "UT1": 3,
        "Mid-Term": 6,
        "UT2": 9,
        "End-Term": 12,
    }

    # Restricting week choices based on exam phase so the scenario stays logically realistic.
    if pred_phase in exam_week_map:
        # Fixing the week for exam phases.
        pred_week = st.selectbox(
            "Week",
            [exam_week_map[pred_phase]],
            help="Week number used as part of the demand scenario.",
        )
    else:
        # Collecting valid regular weeks when the user selects the Regular phase.
        regular_weeks = sorted(data[data["exam_phase"] == "Regular"]["week"].unique())

        # Letting the user choose one of the valid regular weeks.
        pred_week = st.selectbox(
            "Week",
            regular_weeks,
            help="Week number used as part of the demand scenario.",
        )

    # Looking up the default capacity for the selected resource.
    suggested_capacity = resource_capacity_map.get(pred_resource, 5)

    # Creating a capacity input with a resource-specific default value.
    # Important syntax: help=... creates the tooltip icon beside the label.
    pred_capacity = st.number_input(
        "Effective Capacity",
        min_value=1,
        max_value=25,
        value=suggested_capacity,
        help=(
            "The practical number of simultaneous bookings this resource can handle under normal conditions.\n\n"
            "This is not room size. It represents the usable demand limit for this scenario."
        ),
    )

    # Showing whether the chosen slot is usually a high-pressure time window.
    st.caption(f"Typical high-pressure window: {'Yes' if pred_slot in ['Peak_6_8', 'Peak_9_12'] else 'No'}")

    # Building a one-row input DataFrame for model prediction.
    input_data = pd.DataFrame(
        [
            {
                "effective_capacity": pred_capacity,
                "week": pred_week,
                "resource_type": pred_resource,
                "day_of_week": pred_day,
                "time_slot": pred_slot,
                "exam_phase": pred_phase,
            }
        ]
    )

    # One-hot encoding the categorical columns so the input matches the training feature space.
    # Important syntax: pd.get_dummies(...) turns categories into binary indicator columns.
    input_encoded = pd.get_dummies(input_data)

    # Reordering and filling the encoded columns to match the exact training feature order.
    if feature_columns is not None:
        # Important syntax: reindex(columns=..., fill_value=0) ensures missing training columns are added back as zeroes.
        input_encoded = input_encoded.reindex(columns=feature_columns, fill_value=0)
    else:
        # Falling back to the model's recorded feature_names_in_ if available.
        if hasattr(model, "feature_names_in_"):
            # Reordering columns to the order expected by the model.
            input_encoded = input_encoded.reindex(columns=model.feature_names_in_, fill_value=0)

    # Creating the simulation button so prediction runs only after the user clicks it.
    simulate_clicked = st.button("Run Simulation", use_container_width=True)

    # Running the prediction logic only after the button is clicked.
    if simulate_clicked:
        # Using the deployed model to predict booking requests.
        predicted_requests = float(model.predict(input_encoded)[0])

        # Preventing negative booking-request predictions.
        predicted_requests = max(0.0, predicted_requests)

        # Calculating the predicted pressure score as demand divided by capacity.
        predicted_pressure = predicted_requests / pred_capacity

        # Converting the exact decimal prediction into a business-friendly range.
        demand_range_text = format_demand_range(predicted_requests)

        # Converting the pressure score into a readable label.
        predicted_pressure_label = pressure_band_label(predicted_pressure)

        # Opening a styled result box for the simulation output.
        st.markdown('<div class="result-box">', unsafe_allow_html=True)

        # Rendering the expected demand value in a more human-friendly way.
        st.markdown(
            f"""
            <div class="mini-label">Expected Demand</div>
            <div class="big-value">{demand_range_text}</div>
            <div class="helper-text">Estimated booking demand for the selected scenario.</div>
            """,
            unsafe_allow_html=True,
        )

        # Rendering the predicted capacity pressure with a business label.
        st.markdown(
            f"""
            <div style="margin-top:0.9rem;">
                <div class="mini-label">Expected Capacity Pressure</div>
                <div class="big-value">{predicted_pressure:.2f} · {predicted_pressure_label}</div>
                <div class="helper-text">Calculated as expected demand divided by effective capacity.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Displaying an office-friendly action message depending on the predicted pressure.
        if predicted_pressure >= 1.60:
            # Showing an overloaded scenario message.
            st.error("Expected demand exceeds comfortable operating capacity in this scenario. Action is likely needed to prevent bottlenecks or access issues.")
        elif predicted_pressure >= 0.80:
            # Showing a near-capacity message.
            st.warning("This resource is operating near capacity under the selected conditions. Consider monitoring this slot closely or adding flexible capacity if needed.")
        elif predicted_pressure >= 0.50:
            # Showing a healthy but active message.
            st.success("This scenario appears active but manageable within current capacity.")
        else:
            # Showing a clearly low-usage message.
            st.success("Expected demand remains well below capacity. This resource still has room to absorb additional usage if needed.")

        # Closing the styled result box.
        st.markdown("</div>", unsafe_allow_html=True)

    # Closing the right-side glass-card container.
    st.markdown("</div>", unsafe_allow_html=True)

# Creating a collapsible section for technical model information so the main dashboard stays clean for office users.
with st.expander("Technical Model Details"):
    # Showing one short introductory line so the section feels connected to the product story.
    st.markdown(
        """
        <div class="tech-note">
            The dashboard uses a forecasting model to estimate demand and convert it into capacity pressure for operational decision-making.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Checking whether metrics were successfully loaded.
    if metrics_payload:
        # Extracting the per-model metrics dictionary.
        perf = metrics_payload.get("metrics", {})

        # Initializing a list to collect rows for the technical comparison table.
        rows = []

        # Looping through each model and its metrics.
        for model_name, values in perf.items():
            # Appending a clean comparison row for each model.
            rows.append(
                {
                    "Model": model_name,
                    "RMSE": values.get("rmse", None),
                    "MAE": values.get("mae", None),
                    "R2": values.get("r2", None),
                }
            )

        # Converting the list of rows into a DataFrame and sorting by RMSE.
        perf_df = pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)

        # Extracting residuals if they were saved in the metrics payload.
        residuals = metrics_payload.get("residuals", [])

        # Creating two compact columns so the deployed-model table and residual chart sit next to each other.
        tech_left, tech_right = st.columns([1.15, 1], gap="large")

        # Building the left side with deployed model info and compact performance table.
        with tech_left:
            # Showing the currently deployed model name.
            st.markdown(
                f"""
                <div class="tech-subtitle">Deployed Model: {best_model_name}</div>
                """,
                unsafe_allow_html=True,
            )

            # Displaying the model-comparison table in a compact way.
            st.dataframe(
                perf_df,
                use_container_width=True,
                hide_index=True,
                height=215,
            )

        # Building the right side with the residual chart.
        with tech_right:
            # Plotting residuals only if they exist and are in list form.
            if isinstance(residuals, list) and len(residuals) > 0:
                # Creating a small DataFrame for residual plotting.
                residual_df = pd.DataFrame({"Residual": residuals})

                # Building a histogram of residual errors.
                fig_residual = px.histogram(
                    residual_df,
                    x="Residual",
                    nbins=24,
                    title="Residual Error Distribution",
                )

                # Styling the histogram to match the dashboard's dark theme while keeping it compact.
                fig_residual.update_layout(
                    height=260,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(13,23,39,0.96)",
                    font_color="#eef4ff",
                    margin=dict(l=10, r=10, t=50, b=10),
                    title_font=dict(size=18),
                    xaxis_title="Residual",
                    yaxis_title="Count",
                    xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                )

                # Displaying the residual histogram.
                st.plotly_chart(fig_residual, use_container_width=True)
            else:
                # Showing a note if residuals are unavailable.
                st.info("Residual data is not available in the metrics file.")

        # Showing the pressure guide below both side-by-side components.
        st.markdown(
            """
            <div class="guide-box">
                <div class="guide-title">Capacity Pressure Guide</div>
                <div class="guide-text">
                    Under 0.5 = Underused | 0.5–0.8 = Healthy | 0.8–1.6 = Near Capacity | Above 1.6 = Overloaded
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Showing a note if no metrics file is found yet.
    else:
        st.info("No technical metrics file found yet. Run `python train_model.py` to generate one.")