from .models import User
from sqlalchemy.orm import Session
from .schemas import UserBase

def get_users(db: Session):
    """Retrieve all users from the database"""
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    """Retrieve a user by their ID"""
    return db.query(User).filter(User.user_id == user_id).first()

def create_user(db: Session, user: UserBase):
    """Create a new user in the database"""
    db_user = User(
        name=user.name,
        email=user.email,
        status=user.status,
        phone=user.phone,
        registration_date=user.registration_date
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user