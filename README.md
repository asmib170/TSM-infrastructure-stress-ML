TSM (True School of Music) Infrastructure Stress Prediction System

Project Overview:-
This project was developed as part of Hackathon 3, which focuses on converting machine learning models into usable, maintainable systems rather than standalone notebooks.
The objective of this system is to analyze and predict infrastructure demand and stress at the True School of Music (TSM) by modeling usage patterns for limited resources such as:
1. Music Practice Rooms (MPRs – Equipped, Basic, Moldy)
2. Music Production Labs
3. Live Room
4. Studio
The project demonstrates a complete ML engineering lifecycle including:
1. Synthetic data generation
2. SQL-based storage
3. Feature engineering
4. Multi-model training & comparison
5. Automated best-model selection
6. Model serialization
7. Explainability & diagnostics
8. Interactive dashboard deployment
9. Version control and maintainability

----------------------------------

Problem Statement:-
TSM operates with limited music infrastructure. During peak academic periods (especially exam weeks), demand for well-equipped spaces increases sharply.
Some resources are consistently overbooked while others remain underutilized due to:
1. Equipment availability
2. Room condition (e.g., moldy rooms)
3. Time-slot demand patterns
4. Academic calendar effects
Currently, there is no data-driven way to:
1. Quantify infrastructure stress
2. Compare demand patterns across resources
3. Predict booking demand during peak periods
4. Identify bottlenecks
This system addresses that gap by modeling booking demand and computing stress scores (demand ÷ capacity) to support planning and decision-making.

Data Description:-
Since real booking data is not publicly available, synthetic data is generated to realistically simulate student usage behavior.
Synthetic data allows:
1. Privacy preservation
2. Controlled simulation of exam demand spikes
3. Repeatable experimentation
4. Weekly retraining scenarios
The dataset includes:
1. Resource type
2. Effective capacity
3. Academic week (12-week term)
4. Day of week
5. Time slot (Morning, Afternoon, Peak 6–8 PM, Peak 9–12 AM)
6. Exam phase (Regular, UT1, Mid-Term, UT2, End-Term)
7. Booking requests (target variable)
8. Computed stress score (booking_requests ÷ capacity)
All data is stored in an SQLite database to simulate a production-style data pipeline.

Machine Learning Models:-
Five machine learning models were trained and evaluated:
1. Linear Regression
2. Decision Tree Regressor
3. Random Forest Regressor
4. XGBoost Regressor
5. CatBoost Regressor
Models were evaluated using:
1. RMSE (Root Mean Squared Error)
2. MAE (Mean Absolute Error)
3. R² Score (Coefficient of Determination)
The system automatically selects the best-performing model based on lowest RMSE.
Currently, CatBoost demonstrates the strongest overall performance and is deployed as the active prediction model.

Model Diagnostics & Explainability:-
The system includes:
1. Model comparison table (RMSE / MAE / R²)
2. Residual error distribution (Actual − Predicted)
3. Feature importance visualization
4. Automatic best-model deployment
This ensures the system is not only predictive but also interpretable and maintainable.

Dashboard & Prediction System:-
The Streamlit dashboard provides:
1. Infrastructure usage preview
2. Stress analysis by resource type
3. Week & exam-phase filtered analysis
4. Demand prediction interface
Prediction flow:
1. User selects resource, time slot, exam phase, week, and capacity
2. Model predicts booking demand
3. Stress score is computed dynamically
The dashboard always reflects the latest retrained model.

Model Lifecycle & Maintenance:-
The system supports realistic ML lifecycle management:
1. New data can be appended weekly using data_generator.py
2. The model can be retrained using train_model.py
3. Best-performing model is automatically redeployed
4. Evaluation metrics and residual diagnostics update dynamically
This mirrors real-world ML system maintenance.

Project Structure
TSM-infrastructure-stress-ML
│
├── data_generator.py      # Generates synthetic infrastructure usage data
├── train_model.py         # Trains and evaluates ML models
├── dashboard.py           # Streamlit dashboard for analysis and prediction
├── dataset.py             # Data preparation pipeline
├── check_db.py            # Utility to inspect SQLite tables
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
├── models/                # Stored trained models (ignored in Git)
└── .gitignore             # Ignores DB and model artifacts

How to Run:-
1. Install dependencies:
pip install -r requirements.txt
2. Generate synthetic data:
python data_generator.py
3. Train models and select best model:
python train_model.py
4. Launch dashboard:
python -m streamlit run dashboard.py

Key Takeaways:-
1. Demonstrates full ML engineering pipeline (not just model training)
2. Uses SQL instead of static CSV files
3. Supports retraining and lifecycle management
4. Implements boosting models (XGBoost & CatBoost)
5. Includes evaluation diagnostics and explainability
6. Provides a prediction-ready interactive dashboard
7. Designed around a real university infrastructure planning problem


## Model Versioning & Drift Monitoring

This system implements structured weekly model maintenance.

Each retraining cycle includes:

- Synthetic data regeneration
- Multi-model retraining
- Automated best-model selection (lowest RMSE)
- Version logging in `model_registry.json`
- Drift monitoring using Population Stability Index (PSI)
- Weekly drift snapshots stored in `/reports`

### Versioning Strategy
Model versions follow semantic format:

v1.0.x → Incremented automatically after each retraining cycle.

Each version logs:
- Model name
- Target variable
- RMSE, MAE, R²
- Data source
- Update notes
- Timestamp

This ensures transparent tracking of model performance progression.

### Drift Monitoring

Drift is computed using PSI between historical and recent data windows.

Interpretation:
- PSI < 0.1 → No significant drift
- 0.1–0.2 → Moderate drift
- > 0.2 → Significant drift

This ensures the deployed model remains reliable under changing usage patterns (e.g., exam phase demand spikes).


## Current Best Model

Model: CatBoost  
Target: booking_requests  
RMSE: 1.3408  
MAE: 1.0646  
R²: 0.7969  

Deployed automatically after retraining.

Author:
Asmi B.

Hackathon 3 – Machine Learning Systems




