import math
from datetime import date, datetime
from decimal import Decimal

import requests
import dlt
from sqlalchemy import text

from config import MOCK_SERVER_URL, DATABASE_URL
from database import engine

UPSERT_CUSTOMERS_SQL = text("""
INSERT INTO customers (
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    address,
    date_of_birth,
    account_balance,
    created_at
) VALUES (
    :customer_id,
    :first_name,
    :last_name,
    :email,
    :phone,
    :address,
    :date_of_birth,
    :account_balance,
    :created_at
)
ON CONFLICT (customer_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    address = EXCLUDED.address,
    date_of_birth = EXCLUDED.date_of_birth,
    account_balance = EXCLUDED.account_balance,
    created_at = EXCLUDED.created_at
""")


def normalize_customer(customer):
    """Convert JSON payload values into database-friendly Python types."""
    normalized = customer.copy()

    dob = normalized.get("date_of_birth")
    if dob:
        normalized["date_of_birth"] = date.fromisoformat(dob)

    created_at = normalized.get("created_at")
    if created_at:
        normalized["created_at"] = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

    balance = normalized.get("account_balance")
    if balance is not None:
        normalized["account_balance"] = Decimal(str(balance))

    return normalized


def fetch_all_customers():
    """Fetch all customers from Flask mock server, handling pagination."""
    all_customers = []
    page = 1
    limit = 10

    while True:
        response = requests.get(
            f"{MOCK_SERVER_URL}/api/customers",
            params={"page": page, "limit": limit}
        )
        response.raise_for_status()
        data = response.json()

        all_customers.extend(normalize_customer(customer) for customer in data["data"])

        total_pages = math.ceil(data["total"] / limit)
        if page >= total_pages:
            break
        page += 1

    return all_customers


def upsert_customers(customers):
    with engine.begin() as connection:
        connection.execute(UPSERT_CUSTOMERS_SQL, customers)


def cleanup_staging():
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS customers_staging"))


def run_pipeline():
    """Fetch customers, land them with dlt, then upsert into PostgreSQL."""
    customers = fetch_all_customers()
    pipeline_name = f"customer_pipeline_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

    pipeline = dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=dlt.destinations.postgres(DATABASE_URL),
        dataset_name="public"
    )

    pipeline.run(
        customers,
        table_name="customers_staging",
        write_disposition="replace"
    )

    upsert_customers(customers)
    cleanup_staging()
    pipeline.drop()

    return len(customers)
