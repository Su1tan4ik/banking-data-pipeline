import csv
from datetime import date
from getpass import getpass
from pathlib import Path

import psycopg

PROJECT_DIR = Path(__file__).resolve().parent
FILE_PATH = PROJECT_DIR / "data" / "customers.csv"

customers = []

with FILE_PATH.open(newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        customers.append((
            int(row["customer_id"]),
            row["customer_name"],
            row["city"],
            date.fromisoformat(row["registration_date"]),
        ))

password = getpass("PostgreSQL password: ")

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="banking_dwh",
    user="postgres",
    password=password,
) as connection:
    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO customers (
                customer_id,
                customer_name,
                city,
                registration_date
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (customer_id) DO UPDATE SET
                customer_name = EXCLUDED.customer_name,
                city = EXCLUDED.city,
                registration_date = EXCLUDED.registration_date;
            """,
            customers,
        )

        cursor.execute("SELECT COUNT(*) FROM customers;")
        total = cursor.fetchone()[0]

print(f"Processed CSV rows: {len(customers)}")
print(f"Total customers in database: {total}")