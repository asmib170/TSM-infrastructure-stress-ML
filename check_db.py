# Importing sqlite3 to connect to the database
import sqlite3

# Using the exact same DB path as dashboard.py
DB_NAME = r"C:\Users\batto\OneDrive\Desktop\TSM_infrastructure_stress_ML\tsm_infrastructure.db"

# Connecting to SQLite
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Fetching all table names
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

# Printing the result
print("Tables in DB:", tables)

# Closing connection
conn.close()
