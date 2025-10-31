from fastapi import FastAPI, HTTPException, Depends
from typing import List

app = FastAPI(title="Provider Service")

@app.get("/catalog/health")
async def health():
    return {
        "service": "provider-service",
        "status": "healthy"
    }