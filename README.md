TSM Infrastructure Stress Prediction System

Project Overview:
This project was developed as part of Hackathon 3, which focuses on converting machine learning models into usable, maintainable systems rather than standalone notebooks.
The objective of this project is to analyze and predict infrastructure stress at the True School of Music (TSM) by modeling demand patterns for limited resources such as Music Practice Rooms (MPRs), Music Production Labs, the Live Room, and the Studio.
The system demonstrates a complete ML engineering pipeline including data generation, SQL-based storage, model training, prediction readiness, dashboarding, and version control.

Problem Statement:
TSM has limited music infrastructure, and during peak academic periods (especially near exams), demand for well-equipped spaces increases sharply. Some resources are consistently overbooked while others remain underutilized due to factors such as equipment availability or room conditions.
Currently, there is no data-driven way to:
1. Measure infrastructure stress
2. Compare demand across resources
3. Predict future stress levels based on usage patterns
This project addresses that gap by modeling infrastructure usage and predicting stress scores to support better planning and decision-making.

Data Description:
Since real booking data is not publicly available, synthetic data is generated to realistically reflect student usage behavior.
Synthetic data because:
1. Ensures privacy
2. Allows controlled simulation of peak demand scenarios
3. Enables repeatable experiments without static CSV files
The data includes:
1. Resource type (MPR, Studio, Lab, etc.)
2. Effective capacity
3. Academic week (12-week term)
4. Day of week and time slot
5. Exam phase (UT1, Mid-Term, UT2, End-Term)
6. Booking requests
7. Computed stress score (demand ÷ capacity)
All data is stored in an SQLite database, simulating a production-style data pipeline.

Machine Learning Models:
Three traditional machine learning models were trained and evaluated:
1. Linear Regression
2. Decision Tree Regressor
3. Random Forest Regressor
Model performance was compared using RMSE, and the Random Forest model was selected as the final model due to its superior performance and ability to capture non-linear demand patterns.
The trained model is serialized using pickle and loaded dynamically by the dashboard for real-time predictions.

Dashboard & Predictions:
A Streamlit dashboard provides:
1. Preview of infrastructure usage data
2. Visualization of average stress scores by resource type
3. Interactive prediction interface where users can:
 a. Select resource type, time slot, exam phase, and week
 b. Input expected booking requests
 c. Receive a predicted infrastructure stress score
This makes the model prediction-ready and usable.

Model Lifecycle & Maintenance:
The system is designed to support a realistic ML lifecycle:
1. New data can be generated periodically using data_generator.py
2. The model can be retrained using train_model.py
3. Updated models can be deployed without changing the dashboard logic
This mirrors real-world ML workflows where data evolves over time and models require maintenance.

Project Structure:
TSM-infrastructure-stress-ML
│
├── data_generator.py      # Generates synthetic infrastructure usage data
├── train_model.py         # Trains and evaluates ML models
├── dashboard.py           # Streamlit dashboard for analysis and prediction
├── check_db.py            # Utility to inspect SQLite tables
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
├── models/                # Stores trained models (ignored in Git)
└── .gitignore             # Ignores generated DB and model files

How to Run the Project:
1. Install dependencies
pip install -r requirements.txt

2. Generate data
python data_generator.py

3. Train the model
python train_model.py

4. Launch the dashboard
streamlit run dashboard.py

Key Takeaways:
Demonstrates end-to-end ML engineering, not just model training
Uses SQL for data storage instead of static files
Supports retraining and lifecycle management
Provides an interactive, prediction-ready UI
Built specifically around a university-relevant problem

Author:
Asmi B.
Hackathon 3 – Machine Learning Systems
