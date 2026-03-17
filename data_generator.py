# Importing the SQLite library to enable database creation and interaction.
import sqlite3

# Importing the random library to generate synthetic usage data.
import random

# Importing os so I can save the database file in the same folder as this script.
import os


# Database setup

# Naming the SQLite database file to store infrastructure data.
DB_NAME = os.path.join(os.path.dirname(__file__), "tsm_infrastructure.db")

# Creating a connection to the SQLite database.
conn = sqlite3.connect(DB_NAME)

# Creating a cursor object to execute SQL queries on the database.
cursor = conn.cursor()


# Creating table

# Executing an SQL command to create the infrastructure_usage table if it does not already exist.
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

# Committing the table creation changes to the database.
conn.commit()


# Resetting old data

# Deleting existing rows so the synthetic data does not keep duplicating every time I run this script.
cursor.execute("DELETE FROM infrastructure_usage")

# Committing the deletion changes to the database.
conn.commit()


# Resource configuration

# Defining how many actual rooms or units exist under each resource type.
# Important logic: this reflects the real setup you described.
resource_room_counts = {
    "MPR_Equipped": 2,
    "MPR_Basic": 2,
    "MPR_Moldy": 1,
    "MP_Lab": 1,
    "Live_Room": 1,
    "Studio": 1
}

# Defining the effective capacity for each resource type.
# Important logic: this is the practical usable capacity per room/unit.
resource_capacities = {
    "MPR_Equipped": 6,
    "MPR_Basic": 6,
    "MPR_Moldy": 5,
    "MP_Lab": 8,
    "Live_Room": 10,
    "Studio": 12
}

# Defining resource demand weights so overall busyness and pressure tend to follow:
# MPR_Equipped > MPR_Basic > Studio > Live_Room > MP_Lab > MPR_Moldy
# Important logic: MPR_Equipped is intentionally strongest and Moldy is intentionally weakest.
resource_demand_weights = {
    "MPR_Equipped": 1.52,
    "MPR_Basic": 1.10,
    "Studio": 1.02,
    "Live_Room": 0.95,
    "MP_Lab": 0.90,
    "MPR_Moldy": 0.42
}

# Defining the days of the week for usage simulation.
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Defining the daily time slots for infrastructure usage.
time_slots = ["Morning", "Afternoon", "Peak_6_8", "Gap_8_9", "Peak_9_12"]

# Defining day-level multipliers so some days are naturally a bit busier.
day_multipliers = {
    "Mon": 0.95,
    "Tue": 1.00,
    "Wed": 1.03,
    "Thu": 1.05,
    "Fri": 1.02,
    "Sat": 0.92,
    "Sun": 0.82
}

# Defining time-slot multipliers so evening practice windows carry more demand.
time_slot_multipliers = {
    "Morning": 0.72,
    "Afternoon": 0.92,
    "Gap_8_9": 1.02,
    "Peak_6_8": 1.22,
    "Peak_9_12": 1.30
}

# Defining exam-phase multipliers so the demand order tends to be:
# End-Term > Mid-Term > UT2 > UT1 > Regular
exam_phase_multipliers = {
    "Regular": 1.00,
    "UT1": 1.08,
    "UT2": 1.15,
    "Mid-Term": 1.24,
    "End-Term": 1.34
}


# Exam phase mapping (12-week term)

# Defining a function to map academic weeks to examination phases.
def get_exam_phase(week):
    # Checking if the week corresponds to Unit Test 1.
    if week == 3:
        return "UT1"

    # Checking if the week corresponds to Mid-Term examinations.
    elif week == 6:
        return "Mid-Term"

    # Checking if the week corresponds to Unit Test 2.
    elif week == 9:
        return "UT2"

    # Checking if the week corresponds to End-Term examinations.
    elif week == 12:
        return "End-Term"

    # Assigning Regular phase to all non-exam weeks.
    else:
        return "Regular"


# Creating a helper function to generate booking demand in a realistic but controlled way.
def generate_booking_requests(resource, capacity, day, slot, exam_phase):
    # Generating a base level of demand before applying scenario multipliers.
    # Important logic: this higher range helps the system feel active enough overall.
    base_demand = random.uniform(3.8, 5.4)

    # Looking up the resource-specific demand tendency.
    resource_factor = resource_demand_weights[resource]

    # Looking up the day-of-week effect.
    day_factor = day_multipliers[day]

    # Looking up the time-slot effect.
    slot_factor = time_slot_multipliers[slot]

    # Looking up the exam-phase effect.
    exam_factor = exam_phase_multipliers[exam_phase]

    # Multiplying all core demand drivers together.
    raw_demand = base_demand * resource_factor * day_factor * slot_factor * exam_factor

    # Adding small random noise so the data does not feel too engineered.
    noise = random.uniform(-0.9, 1.6)

    # Adding an extra boost for exam-season evening peak slots.
    # Important logic: this makes peak demand windows and exam periods visibly stronger.
    if exam_phase != "Regular" and slot in ["Peak_6_8", "Peak_9_12"]:
        raw_demand += random.uniform(1.2, 2.8)

    # Adding a mild overflow boost to the gap hour.
    if slot == "Gap_8_9":
        raw_demand += random.uniform(0.2, 0.9)

    # Softly suppressing moldy room demand so it stays the least used and least pressured.
    if resource == "MPR_Moldy":
        raw_demand -= random.uniform(1.2, 2.0)

    # Combining the core demand signal with the random noise.
    booking_requests = raw_demand + noise

    # Preventing negative bookings and converting to a whole-number request count.
    booking_requests = max(0, round(booking_requests))

    # Allowing some overload beyond capacity so pressure scenarios appear naturally.
    # Important logic: this keeps the dashboard interesting without becoming absurd.
    booking_requests = min(booking_requests, capacity + 6)

    # Returning the final booking demand.
    return booking_requests


# Generating synthetic data

# Initializing an empty list to store generated infrastructure records.
records = []

# Iterating through each week in the 12-week academic term.
for week in range(1, 13):
    # Determining the exam phase for the current week.
    exam_phase = get_exam_phase(week)

    # Iterating through each day of the week.
    for day in days:
        # Iterating through each time slot of the day.
        for slot in time_slots:
            # Iterating through each resource type and its number of physical rooms.
            for resource, room_count in resource_room_counts.items():
                # Looking up the usable capacity for this resource type.
                capacity = resource_capacities[resource]

                # Generating one record per physical room so room counts affect total usage naturally.
                for _ in range(room_count):
                    # Generating booking requests for this exact scenario.
                    booking_requests = generate_booking_requests(
                        resource=resource,
                        capacity=capacity,
                        day=day,
                        slot=slot,
                        exam_phase=exam_phase
                    )

                    # Calculating the stress score as booking demand divided by effective capacity.
                    stress_score = round(booking_requests / capacity, 2)

                    # Appending the generated row to the records list.
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

# Executing a bulk insert of all generated records into the database table.
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

# Committing the inserted records to the database.
conn.commit()

# Closing the database connection after successful insertion.
conn.close()

# Displaying a confirmation message after data generation is complete.
print("Synthetic TSM infrastructure data generated and stored in SQLite.")