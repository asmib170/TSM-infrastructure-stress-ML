import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "tsm_infrastructure.db")
print("DB_PATH:", os.path.abspath(db_path))

con = sqlite3.connect(db_path)
tables = con.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("TABLES:", tables)
con.close()