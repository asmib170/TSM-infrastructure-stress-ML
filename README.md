🎵 TSM Infrastructure Capacity Intelligence System

Project Overview

This project was developed as part of Hackathon 3, focusing on transforming machine learning models into usable, interpretable, and maintainable systems rather than standalone notebooks.

The system analyzes and predicts infrastructure demand and capacity pressure at the True School of Music (TSM), modeling usage patterns for limited resources such as:

- Music Practice Rooms (MPR – Equipped, Basic, Moldy)
- Music Production Labs
- Live Room
- Studio

It demonstrates a complete ML system pipeline, including:

- Synthetic data generation
- SQL-based storage
- Feature engineering
- Multi-model training & comparison
- Automated best-model selection
- Model versioning & registry tracking
- Drift monitoring (PSI)
- Interactive decision dashboard

---

Problem Statement

TSM operates with limited music infrastructure, and demand spikes during peak academic periods, especially exam weeks.

Challenges

- High demand for equipped spaces during peak hours
- Underutilization of certain resources such as moldy rooms
- No structured way to measure or predict infrastructure stress

Current Gaps

- Quantify capacity pressure
- Compare demand across resources
- Predict booking demand
- Identify operational bottlenecks

This system solves that by modeling booking demand and computing:

Capacity Pressure = Demand ÷ Effective Capacity

---

Data Description

Since real booking data is unavailable, synthetic data is generated to simulate realistic student behavior.

This enables:

- Privacy-safe experimentation
- Controlled exam-period demand spikes
- Repeatable retraining cycles

Dataset includes:

- Resource type
- Effective capacity
- Week (12-week academic cycle)
- Day of week
- Time slot (Morning, Afternoon, Peak hours)
- Exam phase (Regular, UT1, Mid-Term, UT2, End-Term)
- Booking requests (target variable)
- Stress score (demand ÷ capacity)

All data is stored in SQLite, mimicking a production-style pipeline.

---

Machine Learning Models

The system trains and evaluates:

- Linear Regression
- Decision Tree
- Random Forest
- XGBoost
- CatBoost (Best Model)

Evaluation Metrics

- RMSE
- MAE
- R²
- WAPE (Weighted Absolute Percentage Error)

WAPE is used instead of MAPE because it provides stable percentage-based error even when demand values are very small or zero.

The system automatically selects the best-performing model based on lowest RMSE.

---

Current Best Model

Model: CatBoost  
Target: booking_requests  

Metric | Before | Current  
------ | ------ | --------  
RMSE   | 1.34   | 0.97  
MAE    | 1.06   | 0.80  
R²     | 0.79   | 0.87  
WAPE   | —      | ~13–14%  

Significant improvement after refining data realism and retraining.

---

Capacity Pressure Interpretation

- < 0.5 → Underused  
- 0.5 – 0.8 → Healthy  
- 0.8 – 1.6 → Near Capacity  
- > 1.6 → Overloaded  

---

Dashboard and Decision System

Dashboard Insights

- Total demand observed
- Capacity pressure across resources
- Peak usage time windows
- Exam-phase demand trends

Key Feature

Identifies which resource TSM should act on first based on pressure analysis.

Capacity Planning Simulator

Users can:

1. Select resource, time slot, exam phase, week, and capacity  
2. Predict demand using the trained model  
3. Evaluate resulting capacity pressure  

This enables what-if scenario planning for infrastructure decisions.

---

Model Lifecycle and Maintenance

- Weekly synthetic data regeneration
- Retraining with updated data
- Automatic best-model selection
- Version tracking via model_registry.json
- Drift monitoring using PSI

---

Model Versioning and Drift Monitoring

Versioning Strategy

Model versions follow:

v1.0.x

Each version logs:

- Model name
- Metrics (RMSE, MAE, R², WAPE)
- Data source
- Timestamp

Latest version: v1.0.11

Drift Monitoring (PSI)

- PSI < 0.1 → Stable  
- 0.1 – 0.2 → Moderate drift  
- > 0.2 → Significant drift  

---

Project Structure

TSM-INFRASTRUCTURE-STRESS-ML/
│
├── Data/
│   ├── data_generator.py
│   └── dataset.py
│
├── Model/
│   ├── train_model.py
│   ├── registry_utils.py
│   └── model_registry.json
│
├── Dashboard/
│   └── dashboard.py
│
├── Monitoring/
│   └── drift_report.py
│
├── Database/
│   ├── check_db.py
│   └── debug_db.py
│
├── artifacts/
│   ├── best_model.pkl
│   └── metrics.json
│
├── reports/
│   └── drift/
│
├── requirements.txt
├── README.md

---

How to Run

pip install -r requirements.txt  
python -m Data.data_generator  
python -m Model.train_model  
python -m streamlit run Dashboard/dashboard.py  

Optional:  
python -m Monitoring.drift_report  

---

Key Takeaways

- End-to-end ML system (not just model training)  
- Realistic synthetic data simulation  
- SQL-based pipeline  
- Model versioning and tracking  
- Drift monitoring integration  
- Interactive decision dashboard  
- Strong alignment with real-world infrastructure planning  

---

Author

Asmi B.  
Hackathon 3 – Machine Learning Systems