# schema_parser.py

import psycopg2
import re



def get_schema_data(dbname, user, password, host, port):
    # Connect to the database
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Define a function to get schema information
    def get_schema(cursor):
        # Fetch all table names in the schema
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        db_schema = {}

        # Loop through each table and fetch its columns
        for table in tables:
            table_name = table[0]
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,))
            columns = cursor.fetchall()
            columns_list = [col[0] for col in columns]
            db_schema[table_name] = columns_list

        return db_schema

    # Call the function to get the schema
    db_schema = get_schema(cursor)

    # Don't forget to close the cursor and connection when done
    cursor.close()
    conn.close()

    return db_schema







# Define the SQL query
query = """
SELECT e.email, e.phone_number, d.department_name 
FROM employees e 
JOIN departments d ON e.department_id = d.id 
WHERE e.department_id = 3
"""


def extract_columns(query):
    
    select_from_pattern = r'SELECT\s+(.*?)\s+FROM'
    
    join_pattern = r'JOIN\s+\w+\s+\w+\s+ON\s+(.*?)\s+WHERE'
    
    where_pattern = r'WHERE\s+(.*?)$'

    
    columns_select_from = re.findall(select_from_pattern, query, re.IGNORECASE | re.DOTALL)[0].split(',')
    
    columns_join = re.findall(join_pattern, query, re.IGNORECASE | re.DOTALL)
    
    columns_where = re.findall(where_pattern, query, re.IGNORECASE | re.DOTALL)

    
    columns_join = [re.split(r'\s*=\s*', condition.strip()) for condition in columns_join]
    columns_join = [column.strip() for condition in columns_join for column in condition]

    
    columns_where = [re.split(r'\s*=\s*', condition.strip()) for condition in columns_where]
    columns_where = [column.strip() for condition in columns_where for column in condition]

    
    extracted_columns = [column.strip() for column in columns_select_from] + columns_join + columns_where

    return extracted_columns


extracted_columns = extract_columns(query)
print("Extracted Columns:", extracted_columns)

