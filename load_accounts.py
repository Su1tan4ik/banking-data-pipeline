import csv
from getpass import getpass
from pathlib import Path

import psycopg

PROJECT_DIR = Path(__file__).resolve().parent
FILE_PATH = PROJECT_DIR / "data" / "accounts.csv"

accounts = []

with FILE_PATH.open(newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        accounts.append((
            int(row["account_id"]),
            int(row["customer_id"]),
            row["account_type"],
            row["currency"],
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
            INSERT INTO accounts (
                account_id,
                customer_id,
                account_type,
                currency
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (account_id) DO UPDATE SET
                customer_id = EXCLUDED.customer_id,
                account_type = EXCLUDED.account_type,
                currency = EXCLUDED.currency;
            """,
            accounts,
        )

        cursor.execute("SELECT COUNT(*) FROM accounts;")
        total = cursor.fetchone()[0]

print(f"Processed CSV rows: {len(accounts)}")
print(f"Total accounts in database: {total}")