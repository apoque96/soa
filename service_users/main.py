from fastapi import FastAPI, HTTPException, Depends
from . import db, models, services, schemas
from .db import get_db, engine
from sqlalchemy.orm import Session
from typing import List

app = FastAPI(title="Users Service")

@app.get("/users/health")
async def health():
    return {
        "service": "users-service",
        "status": "healthy"
    }

@app.get("/users/", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return services.get_users(db)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = services.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    return services.create_user(db, user)

@app.post("/users/validate")
def validate_user(user_data: dict, db: Session = Depends(get_db)):
    """Validate if a user exists - called by ESB"""
    user_id = user_data.get("user_id")
    
    if not user_id:
        return {
            "valid": False,
            "message": "user_id is required"
        }
    
    user = services.get_user_by_id(db, user_id)
    
    if user is None:
        return {
            "valid": False,
            "message": f"User with id {user_id} does not exist"
        }
    
    return {
        "valid": True,
        "message": "User exists",
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "status": user.status
        }
    }