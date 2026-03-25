from fastapi import FastAPI

from config import MOCK_SERVER_URL, DATABASE_URL

app = FastAPI(title="Customer Pipeline Service")


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "pipeline-service"}
