from fastapi import FastAPI, HTTPException, Depends
from typing import List

app = FastAPI(title="Catalog Service")

@app.get("/catalog/health")
async def health():
    return {
        "service": "catalog-service",
        "status": "healthy"
    }