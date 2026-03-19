# Importing the SQLite library to enable database creation and interaction.
import sqlite3

# Importing the random library to generate synthetic usage data.
import random

# Importing os to handle file paths correctly
import os


# -----------------------------
# PATH SETUP (VERY IMPORTANT FIX)
# -----------------------------

# Getting current file directory (Data folder)
CURRENT_DIR = os.path.dirname(__file__)

# Moving to project root
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# Defining database path in project root (FIXED)
DB_NAME = os.path.join(PROJECT_ROOT, "tsm_infrastructure.db")


# -----------------------------
# DATABASE SETUP
# -----------------------------

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


# -----------------------------
# CREATE TABLE
# -----------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS infrastructure_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_type TEXT,
    effective_capacity INTEGER,
    week INTEGER,
    day_of_week TEXT,
    time_slot TEXT,
    exam_phase TEXT,
    booking_requests INTEGER,
    stress_score REAL
)
""")

conn.commit()


# -----------------------------
# RESET OLD DATA
# -----------------------------

cursor.execute("DELETE FROM infrastructure_usage")
conn.commit()


# -----------------------------
# RESOURCE CONFIGURATION
# -----------------------------

resource_room_counts = {
    "MPR_Equipped": 2,
    "MPR_Basic": 2,
    "MPR_Moldy": 1,
    "MP_Lab": 1,
    "Live_Room": 1,
    "Studio": 1
}

resource_capacities = {
    "MPR_Equipped": 6,
    "MPR_Basic": 6,
    "MPR_Moldy": 5,
    "MP_Lab": 8,
    "Live_Room": 10,
    "Studio": 12
}

resource_demand_weights = {
    "MPR_Equipped": 1.52,
    "MPR_Basic": 1.10,
    "Studio": 1.02,
    "Live_Room": 0.95,
    "MP_Lab": 0.90,
    "MPR_Moldy": 0.42
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

time_slots = ["Morning", "Afternoon", "Peak_6_8", "Gap_8_9", "Peak_9_12"]

day_multipliers = {
    "Mon": 0.95,
    "Tue": 1.00,
    "Wed": 1.03,
    "Thu": 1.05,
    "Fri": 1.02,
    "Sat": 0.92,
    "Sun": 0.82
}

time_slot_multipliers = {
    "Morning": 0.72,
    "Afternoon": 0.92,
    "Gap_8_9": 1.02,
    "Peak_6_8": 1.22,
    "Peak_9_12": 1.30
}

exam_phase_multipliers = {
    "Regular": 1.00,
    "UT1": 1.08,
    "UT2": 1.15,
    "Mid-Term": 1.24,
    "End-Term": 1.34
}


# -----------------------------
# EXAM PHASE LOGIC
# -----------------------------

def get_exam_phase(week):
    if week == 3:
        return "UT1"
    elif week == 6:
        return "Mid-Term"
    elif week == 9:
        return "UT2"
    elif week == 12:
        return "End-Term"
    else:
        return "Regular"


# -----------------------------
# DEMAND GENERATION
# -----------------------------

def generate_booking_requests(resource, capacity, day, slot, exam_phase):

    base_demand = random.uniform(3.8, 5.4)

    resource_factor = resource_demand_weights[resource]
    day_factor = day_multipliers[day]
    slot_factor = time_slot_multipliers[slot]
    exam_factor = exam_phase_multipliers[exam_phase]

    raw_demand = base_demand * resource_factor * day_factor * slot_factor * exam_factor

    noise = random.uniform(-0.9, 1.6)

    if exam_phase != "Regular" and slot in ["Peak_6_8", "Peak_9_12"]:
        raw_demand += random.uniform(1.2, 2.8)

    if slot == "Gap_8_9":
        raw_demand += random.uniform(0.2, 0.9)

    if resource == "MPR_Moldy":
        raw_demand -= random.uniform(1.2, 2.0)

    booking_requests = raw_demand + noise
    booking_requests = max(0, round(booking_requests))
    booking_requests = min(booking_requests, capacity + 6)

    return booking_requests


# -----------------------------
# DATA GENERATION LOOP
# -----------------------------

records = []

for week in range(1, 13):
    exam_phase = get_exam_phase(week)

    for day in days:
        for slot in time_slots:
            for resource, room_count in resource_room_counts.items():
                capacity = resource_capacities[resource]

                for _ in range(room_count):

                    booking_requests = generate_booking_requests(
                        resource,
                        capacity,
                        day,
                        slot,
                        exam_phase
                    )

                    stress_score = round(booking_requests / capacity, 2)

                    records.append((
                        resource,
                        capacity,
                        week,
                        day,
                        slot,
                        exam_phase,
                        booking_requests,
                        stress_score
                    ))


# -----------------------------
# INSERT INTO DATABASE
# -----------------------------

cursor.executemany("""
INSERT INTO infrastructure_usage (
    resource_type,
    effective_capacity,
    week,
    day_of_week,
    time_slot,
    exam_phase,
    booking_requests,
    stress_score
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", records)

conn.commit()
conn.close()

print("Synthetic TSM infrastructure data generated and stored in SQLite.")