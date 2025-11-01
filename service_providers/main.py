from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from . import db, models, services, schemas
from .db import get_db, engine

app = FastAPI(title="Provider Service")

@app.get("/providers/health")
async def health():
    return {
        "service": "provider-service",
        "status": "healthy"
    }

@app.get("/providers/{provider_id}", response_model=schemas.Provider)
async def get_provider(provider_id: int, db: Session = Depends(get_db)):
    db_provider = services.get_provider(db, provider_id)
    if db_provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return db_provider

@app.get("/providers/", response_model=List[schemas.Provider])
async def list_providers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    providers_list = services.get_providers(db, skip=skip, limit=limit)
    return providers_list

@app.post("/providers/", response_model=schemas.Provider)
async def create_provider(provider: schemas.ProviderCreate, db: Session = Depends(get_db)):
    return services.create_provider(db, provider.dict())