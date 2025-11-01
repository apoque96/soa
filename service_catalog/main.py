from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from . import db, models, services, schemas
from .db import get_db, engine

app = FastAPI(title="Catalog Service")

@app.get("/services/health")
async def health():
    return {
        "service": "catalog-service",
        "status": "healthy"
    }

@app.get("/services/{service_id}", response_model=schemas.Service)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    db_service = services.get_service(db, service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

@app.get("/services/", response_model=List[schemas.Service])
async def list_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    services_list = services.get_services(db, skip=skip, limit=limit)
    return services_list

@app.post("/services/", response_model=schemas.Service)
async def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    return services.create_service(db, service.dict())