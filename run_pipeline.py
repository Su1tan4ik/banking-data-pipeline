import csv
import os
from dotenv import load_dotenv
from pathlib import Path

import psycopg
from psycopg import sql

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

TABLES = [
    (
        "customers",
        ["customer_id", "customer_name", "city", "registration_date"],
    ),
    (
        "accounts",
        ["account_id", "customer_id", "account_type", "currency"],
    ),
    (
        "transactions",
        [
            "transaction_id",
            "account_id",
            "transaction_type",
            "amount",
            "currency",
            "status",
            "transaction_date",
        ],
    ),
]


def load_table(cursor, table_name, columns):
    file_path = DATA_DIR / f"{table_name}.csv"

    with file_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != columns:
            raise ValueError(f"Unexpected CSV columns: {file_path.name}")

        rows = [
            tuple(row[column] for column in columns)
            for row in reader
        ]

    if not rows:
        raise ValueError(f"Empty CSV: {file_path.name}")

    primary_key = columns[0]

    updates = sql.SQL(", ").join(
        sql.SQL("{} = EXCLUDED.{}").format(
            sql.Identifier(column),
            sql.Identifier(column),
        )
        for column in columns[1:]
    )

    query = sql.SQL("""
        INSERT INTO {} ({})
        VALUES ({})
        ON CONFLICT ({}) DO UPDATE SET {};
    """).format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(map(sql.Identifier, columns)),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns),
        sql.Identifier(primary_key),
        updates,
    )

    cursor.executemany(query, rows)

    cursor.execute(
        sql.SQL("SELECT COUNT(*) FROM {}").format(
            sql.Identifier(table_name)
        )
    )
    total = cursor.fetchone()[0]

    return len(rows), total

def check_data(cursor):
    checks = [
        (
            "Every customer has exactly two accounts",
            """
            SELECT COUNT(*)
            FROM (
                SELECT c.customer_id
                FROM customers c
                LEFT JOIN accounts a
                    ON c.customer_id = a.customer_id
                GROUP BY c.customer_id
                HAVING COUNT(a.account_id) <> 2
            ) AS invalid_customers;
            """,
        ),
        (
            "Transaction currency matches account currency",
            """
            SELECT COUNT(*)
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE t.currency <> a.currency;
            """,
        ),
        (
            "Transactions occur after customer registration",
            """
            SELECT COUNT(*)
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            JOIN customers c ON a.customer_id = c.customer_id
            WHERE t.transaction_date::date < c.registration_date;
            """,
        ),
        (
            "Daily mart operation count matches source",
            """
            SELECT ABS(
                (SELECT COUNT(*) FROM transactions)
                -
                (SELECT COALESCE(SUM(total_operations), 0)
                 FROM daily_transactions)
            );
            """,
        ),
    ]

    for name, query in checks:
        cursor.execute(query)
        errors = cursor.fetchone()[0]

        if errors != 0:
            raise ValueError(f"FAILED: {name}. Errors: {errors}")

        print(f"PASS: {name}")
load_dotenv(PROJECT_DIR / ".env", interpolate=False)

results = []

with psycopg.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
) as connection:
    with connection.cursor() as cursor:
        for table_name, columns in TABLES:
            processed, total = load_table(cursor, table_name, columns)
            results.append((table_name, processed, total))

        check_data(cursor)

print("Pipeline completed successfully.")

for table_name, processed, total in results:
    print(f"{table_name}: processed={processed}, total={total}")