import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/customer_db")
MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://mock-server:5000")
