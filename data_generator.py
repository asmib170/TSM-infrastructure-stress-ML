# Importing the SQLite library to enable database creation and interaction
import sqlite3

# Importing the random library to generate synthetic usage data
import random


# Database setup

# Naming the SQLite database file to store infrastructure data
import os
DB_NAME = os.path.join(os.path.dirname(__file__), "tsm_infrastructure.db")

# Creating a connection to the SQLite database
conn = sqlite3.connect(DB_NAME)

# Creating a cursor object to execute SQL queries on the database
cursor = conn.cursor()


# Creating table

# Executing an SQL command to create the infrastructure_usage table if it does not already exist
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

# Committing the table creation changes to the database
conn.commit()


# Resetting old data (optional but recommended for clean regeneration)

# Deleting existing rows so the synthetic data does not keep duplicating every time you run this script
cursor.execute("DELETE FROM infrastructure_usage")

# Committing the deletion changes to the database
conn.commit()


# Resource configuration (TSM-specific)

# Defining the available infrastructure resources and their effective capacities
resources = {
    "MPR_Equipped": 2,   # 2 MPRs with mixer + monitors
    "MPR_Basic": 1,      # only 1 usable (others moldy)
    "MPR_Moldy": 2,      # 2 moldy MPRs (rarely used)
    "MP_Lab": 2,
    "Live_Room": 1,
    "Studio": 1
}

# Defining the days of the week for usage simulation
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Defining the daily time slots for infrastructure usage (more precise peak slots)
time_slots = ["Morning", "Afternoon", "Peak_6_8", "Gap_8_9", "Peak_9_12"]


# Exam phase mapping (12-week term)

# Defining a function to map academic weeks to examination phases
def get_exam_phase(week):

    # Checking if the week corresponds to Unit Test 1
    if week == 3:
        return "UT1"

    # Checking if the week corresponds to Mid-Term examinations
    elif week == 6:
        return "Mid-Term"

    # Checking if the week corresponds to Unit Test 2
    elif week == 9:
        return "UT2"

    # Checking if the week corresponds to End-Term examinations
    elif week == 12:
        return "End-Term"

    # Assigning Regular phase to all non-exam weeks
    else:
        return "Regular"


# Generating synthetic data

# Defining the exam phases where peak hours actually spike strongly
EXAM_PEAK_PHASES = {"UT1", "Mid-Term", "UT2", "End-Term"}

# Initializing an empty list to store generated infrastructure records
records = []

# Iterating through each week in the 12-week academic term
for week in range(1, 13):

    # Determining the exam phase for the current week
    exam_phase = get_exam_phase(week)

    # Iterating through each day of the week
    for day in days:

        # Iterating through each time slot of the day
        for slot in time_slots:

            # Iterating through each resource and its capacity
            for resource, capacity in resources.items():

                # Generating a base number of booking requests
                booking_requests = random.randint(0, capacity + 2)

                # Increasing demand during peak practice hours ONLY in exam peak phases
                if exam_phase in EXAM_PEAK_PHASES and slot in ["Peak_6_8", "Peak_9_12"]:
                    booking_requests += random.randint(4, 8)

                # Keeping peaks mild during regular weeks
                elif exam_phase == "Regular" and slot in ["Peak_6_8", "Peak_9_12"]:
                    booking_requests += random.randint(1, 3)

                # Adding mild demand during the gap hour (8–9 PM)
                if slot == "Gap_8_9":
                    booking_requests += random.randint(0, 2)

                # Adding overall exam pressure across the day (smaller than peak boost)
                if exam_phase in EXAM_PEAK_PHASES:
                    booking_requests += random.randint(1, 3)

                # Reducing booking demand for underutilized basic MPRs
                if resource == "MPR_Basic":
                    booking_requests = max(0, booking_requests - 2)

                # Keeping moldy MPR usage near-zero even during peak and exam weeks
                if resource == "MPR_Moldy":
                    booking_requests = random.randint(0, 1)

                # Calculating the stress score as demand-to-capacity ratio
                stress_score = round(booking_requests / capacity, 2)

                # Appending the generated record to the records list
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


# Inserting data into SQLite

# Executing a bulk insert of all generated records into the database table
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

# Committing the inserted records to the database
conn.commit()

# Closing the database connection after successful insertion
conn.close()

# Displaying a confirmation message after data generation is complete
print(" Synthetic TSM infrastructure data generated and stored in SQLite.")
