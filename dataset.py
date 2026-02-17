# Importing sqlite3 to connect to the database
import sqlite3

# Importing pandas to read the SQL table into a DataFrame
import pandas as pd


# Database connection

# Using the exact same DB path as dashboard.py and data_generator.py
DB_NAME = r"C:\Users\batto\OneDrive\Desktop\TSM_infrastructure_stress_ML\tsm_infrastructure.db"

# Connecting to the SQLite database
conn = sqlite3.connect(DB_NAME)

# Reading the infrastructure_usage table into a DataFrame
df = pd.read_sql("SELECT * FROM infrastructure_usage", conn)

# Closing the database connection
conn.close()

# Printing the first and last rows to verify the dataset
print(df.head(10))
print(df.tail(10))
