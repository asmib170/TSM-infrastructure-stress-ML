# 🎵 TSM Infrastructure Capacity Intelligence System

## Project Overview
This project was developed as part of Hackathon 3, focusing on transforming machine learning models into usable, interpretable, and maintainable systems rather than standalone notebooks.

The system analyzes and predicts **infrastructure demand and capacity pressure** at the True School of Music (TSM), modeling usage patterns for limited resources such as:

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

## Problem Statement
TSM operates with limited music infrastructure, and demand spikes during peak academic periods, especially exam weeks.

### Challenges
- High demand for equipped spaces during peak hours
- Underutilization of certain resources such as moldy rooms
- No structured way to measure or predict infrastructure stress

### Current Gaps
- Quantify capacity pressure
- Compare demand across resources
- Predict booking demand
- Identify operational bottlenecks

This system solves that by modeling booking demand and computing:

**Capacity Pressure = Demand ÷ Effective Capacity**

---

## Data Description
Since real booking data is unavailable, synthetic data is generated to simulate realistic student behavior.

### This enables:
- Privacy-safe experimentation
- Controlled exam-period demand spikes
- Repeatable retraining cycles

### Dataset includes:
- Resource type
- Effective capacity
- Week (12-week academic cycle)
- Day of week
- Time slot (Morning, Afternoon, Peak hours)
- Exam phase (Regular, UT1, Mid-Term, UT2, End-Term)
- Booking requests *(target variable)*
- Stress score *(demand ÷ capacity)*

All data is stored in **SQLite**, mimicking a production-style pipeline.

---

## Machine Learning Models
The system trains and evaluates:

- Linear Regression
- Decision Tree
- Random Forest
- XGBoost
- **CatBoost (Best Model)**

### Evaluation Metrics
- RMSE
- MAE
- R²

The system automatically selects the **best-performing model based on lowest RMSE**.

---

## Current Best Model

**Model:** CatBoost  
**Target:** `booking_requests`

| Metric | Before | Current |
|--------|--------|---------|
| RMSE   | 1.34   | **0.96** |
| MAE    | 1.06   | **0.78** |
| R²     | 0.79   | **0.88** |

Significant improvement after refining data realism and retraining.

---

## Capacity Pressure Interpretation
To better reflect real-world operations, pressure is interpreted as:

- **< 0.5 → Underused**
- **0.5 – 0.8 → Healthy**
- **0.8 – 1.6 → Near Capacity**
- **> 1.6 → Overloaded**

This ensures moderately loaded systems are not incorrectly labeled as underutilized.

---

## Dashboard and Decision System

### Dashboard Insights
- Total demand observed
- Capacity pressure across resources
- Peak usage time windows
- Exam-phase demand trends

### Key Feature
Identifies **which resource TSM should act on first**.

### Capacity Planning Simulator
Users can:
1. Select resource, time slot, exam phase, week, and capacity
2. Predict demand using the trained model
3. Evaluate resulting capacity pressure

---

## Model Lifecycle and Maintenance
The system supports a realistic ML lifecycle:

- Weekly synthetic data regeneration
- Retraining with updated data
- Automatic best-model selection
- Version tracking via `model_registry.json`
- Drift monitoring using PSI

---

## Model Versioning and Drift Monitoring

### Versioning Strategy
Model versions follow the format:

`v1.0.x`

Each version logs:
- Model name
- Metrics (RMSE, MAE, R²)
- Data source
- Timestamp

**Latest version:** `v1.0.11`

### Drift Monitoring (PSI)
- **PSI < 0.1** → Stable
- **0.1 – 0.2** → Moderate drift
- **> 0.2** → Significant drift

This helps ensure model reliability across changing usage patterns.

---

## Project Structure

```text
TSM-infrastructure-stress-ML
│
├── data_generator.py
├── train_model.py
├── dashboard.py
├── dataset.py
├── check_db.py
├── requirements.txt
├── README.md
├── models/
└── .gitignore

---
## How to Run

```bash
pip install -r requirements.txt
python data_generator.py
python train_model.py
streamlit run dashboard.py

---

## Key Takeaways

- End-to-end ML system (not just model training)  
- Realistic synthetic data simulation  
- SQL-based pipeline  
- Model versioning and tracking  
- Drift monitoring integration  
- Interactive decision dashboard  
- Strong alignment with real-world infrastructure planning  

---

## Author

**Asmi B.**  
Hackathon 3 – Machine Learning Systems