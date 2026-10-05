import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

cities = ["Almaty", "Astana", "Shymkent", "Karaganda", "Aktobe"]
start_date = date(2024, 1, 1)

file_path = DATA_DIR / "customers.csv"

with file_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "customer_id",
        "customer_name",
        "city",
        "registration_date",
    ])

    for customer_id in range(1, 1001):
        registration_date = start_date + timedelta(
            days=random.randint(0, 730)
        )

        writer.writerow([
            customer_id,
            f"Customer_{customer_id:04d}",
            random.choice(cities),
            registration_date.isoformat(),
        ])

print("Generated 1000 synthetic customers.")
print(f"File saved to: {file_path}")

accounts_path = DATA_DIR / "accounts.csv"

with accounts_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "account_id",
        "customer_id",
        "account_type",
        "currency",
    ])

    account_id = 1

    for customer_id in range(1, 1001):
        for account_type in ["current", "savings"]:
            writer.writerow([
                account_id,
                customer_id,
                account_type,
                "KZT",
            ])

            account_id += 1

print("Generated 2000 synthetic accounts.")
print(f"File saved to: {accounts_path}")

from datetime import datetime

transactions_path = DATA_DIR / "transactions.csv"
transaction_random = random.Random(43)
transaction_start = datetime(2026, 9, 1)

with transactions_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "transaction_id",
        "account_id",
        "transaction_type",
        "amount",
        "currency",
        "status",
        "transaction_date",
    ])

    for transaction_id in range(1, 10001):
        account_id = transaction_random.randint(1, 2000)

        transaction_type = transaction_random.choice([
            "payment",
            "deposit",
        ])

        amount_tiyn = transaction_random.randint(10000, 5000000)
        amount = f"{amount_tiyn // 100}.{amount_tiyn % 100:02d}"

        status = transaction_random.choices(
            ["completed", "failed"],
            weights=[95, 5],
            k=1,
        )[0]

        transaction_date = transaction_start + timedelta(
            seconds=transaction_random.randrange(30 * 24 * 60 * 60)
        )

        writer.writerow([
            transaction_id,
            account_id,
            transaction_type,
            amount,
            "KZT",
            status,
            transaction_date.isoformat(sep=" "),
        ])

print("Generated 10000 synthetic transactions.")
print(f"File saved to: {transactions_path}")