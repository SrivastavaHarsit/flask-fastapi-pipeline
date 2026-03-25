from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from database import engine, Base
from routes.ingest import router as ingest_router
from routes.customers import router as customers_router

app = FastAPI(title="Customer Pipeline Service")

app.include_router(ingest_router)
app.include_router(customers_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "pipeline-service"}


@app.get("/api/health/db")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from exc

    return {
        "status": "healthy",
        "service": "pipeline-service",
        "database": "connected",
    }
