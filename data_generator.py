# Importing the SQLite library to enable database creation and interaction
import sqlite3

# Importing the random library to generate synthetic usage data
import random


# Database setup

# Naming the SQLite database file to store infrastructure data
DB_NAME = r"C:\Users\batto\OneDrive\Desktop\TSM_infrastructure_stress_ML\tsm_infrastructure.db"

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



# Resource configuration (TSM-specific)

# Defining the available infrastructure resources and their effective capacities
resources = {
    "MPR_Equipped": 2,   # 2 MPRs with mixer + monitors
    "MPR_Basic": 1,      # only 1 usable (others moldy)
    "MP_Lab": 2,
    "Live_Room": 1,
    "Studio": 1
}

# Defining the days of the week for usage simulation
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Defining the daily time slots for infrastructure usage
time_slots = ["Morning", "Afternoon", "Evening", "Night"]



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

                # Increasing demand during night-time practice hours
                if slot == "Night":
                    booking_requests += random.randint(2, 5)

                # Increasing demand during examination periods
                if exam_phase != "Regular":
                    booking_requests += random.randint(3, 7)

                # Reducing booking demand for underutilized basic MPRs
                if resource == "MPR_Basic":
                    booking_requests = max(0, booking_requests - 3)

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
