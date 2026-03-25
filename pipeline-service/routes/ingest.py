from fastapi import APIRouter

from services.ingestion import run_pipeline

router = APIRouter()


@router.post("/api/ingest")
def ingest():
    records = run_pipeline()
    return {"status": "success", "records_processed": records}
