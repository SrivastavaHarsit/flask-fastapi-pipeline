import requests
from fastapi import APIRouter, HTTPException

from services.ingestion import run_pipeline

router = APIRouter()


@router.post("/api/ingest")
def ingest():
    try:
        records = run_pipeline()
    except requests.ConnectionError:
        raise HTTPException(status_code=502, detail="Mock server is unreachable")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(exc)}")

    return {"status": "success", "records_processed": records}
