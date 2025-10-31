from fastapi import FastAPI, HTTPException, Depends
from typing import List

app = FastAPI(title="Access Service")

@app.get("/catalog/health")
async def health():
    return {
        "service": "access-service",
        "status": "healthy"
    }