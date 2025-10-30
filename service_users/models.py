import datetime
from .db import Base
from sqlalchemy import Column, Integer, String, DateTime

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    status = Column(String, default="active")
    phone = Column(String, unique=True, index=True)
    registration_date = Column(DateTime, default=datetime.datetime.now)