from sqlalchemy.orm import Session
from . import models

def get_service(db: Session, service_id: int):
    return db.query(models.Service).filter(models.Service.service_id == service_id).first()

def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Service).offset(skip).limit(limit).all()

def create_service(db: Session, service: dict):
    db_service = models.Service(**service)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service