import csv
from datetime import datetime
from decimal import Decimal
from getpass import getpass
from pathlib import Path

import psycopg

PROJECT_DIR = Path(__file__).resolve().parent
FILE_PATH = PROJECT_DIR / "data" / "transactions.csv"

transactions = []

with FILE_PATH.open(newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        transactions.append((
            int(row["transaction_id"]),
            int(row["account_id"]),
            row["transaction_type"],
            Decimal(row["amount"]),
            row["currency"],
            row["status"],
            datetime.fromisoformat(row["transaction_date"]),
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
            INSERT INTO transactions (
                transaction_id,
                account_id,
                transaction_type,
                amount,
                currency,
                status,
                transaction_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO UPDATE SET
                account_id = EXCLUDED.account_id,
                transaction_type = EXCLUDED.transaction_type,
                amount = EXCLUDED.amount,
                currency = EXCLUDED.currency,
                status = EXCLUDED.status,
                transaction_date = EXCLUDED.transaction_date;
            """,
            transactions,
        )

        cursor.execute("SELECT COUNT(*) FROM transactions;")
        total = cursor.fetchone()[0]

print(f"Processed CSV rows: {len(transactions)}")
print(f"Total transactions in database: {total}")