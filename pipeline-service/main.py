from fastapi import FastAPI

app = FastAPI(title="Customer Pipeline Service")


@app.get("/api/health")
def health():
    return {"status": "healthy"}
