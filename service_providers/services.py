from sqlalchemy.orm import Session
from . import models

def get_provider(db: Session, provider_id: int):
    return db.query(models.Provider).filter(models.Provider.provider_id == provider_id).first()

def get_providers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Provider).offset(skip).limit(limit).all()

def create_provider(db: Session, provider: dict):
    db_provider = models.Provider(**provider)
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider