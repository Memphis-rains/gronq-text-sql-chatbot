import psycopg2
import random
from datetime import date, timedelta
from faker import Faker

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname="demoDB",
    user="postgres",
    password="sapan",
    host='localhost',
    port='5432'
)

# Create a cursor object
cursor = conn.cursor()

# Function to create projects
def create_projects():
    projects = [
        ("Project A", date.today() - timedelta(days=30), date.today() + timedelta(days=60)),
        ("Project B", date.today() - timedelta(days=60), date.today() + timedelta(days=90)),
        ("Project C", date.today() - timedelta(days=45), date.today() + timedelta(days=75)),
        ("Project D", date.today() - timedelta(days=90), date.today() + timedelta(days=120)),
        ("Project E", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project F", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project G", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project H", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project I", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project J", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project K", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project L", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project M", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
        ("Project N", date.today() - timedelta(days=75), date.today() + timedelta(days=105)),
    ]
    # Insert projects into the Projects table
    for project in projects:
        cursor.execute("INSERT INTO Projects (name, start_date, end_date) VALUES (%s, %s, %s)", project)

# Commit the projects transaction
conn.commit()

# Create projects
create_projects()

# Get all employee IDs
cursor.execute("SELECT emp_id FROM Employees")
employee_ids = [row[0] for row in cursor.fetchall()]

# Get all project IDs
cursor.execute("SELECT project_id FROM Projects")
project_ids = [row[0] for row in cursor.fetchall()]

# Assign employees to projects with a minimum of 1 and a maximum of 3 projects
for emp_id in employee_ids:
    # Shuffle the list of project IDs
    random.shuffle(project_ids)
    # Determine the number of projects to assign (between 1 and 3)
    num_projects = random.randint(1, 5)
    # Select the first 'num_projects' project IDs
    selected_projects = project_ids[:num_projects]
    # Insert records into the EmployeeProjects table
    for project_id in selected_projects:
        cursor.execute("INSERT INTO EmployeeProjects (emp_id, project_id) VALUES (%s, %s)", (emp_id, project_id))

# Commit the transaction
conn.commit()

# Close cursor and connection
cursor.close()
conn.close()
