from fastapi import FastAPI

from config import MOCK_SERVER_URL, DATABASE_URL
from database import engine, Base
from models.customer import Customer
from services.ingestion import run_pipeline

app = FastAPI(title="Customer Pipeline Service")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "pipeline-service"}


@app.post("/api/ingest")
def ingest():

    records = run_pipeline()
    return {"status": "success", "records_processed": records}
