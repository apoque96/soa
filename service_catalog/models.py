import datetime
from .db import Base
from sqlalchemy import Column, Integer, String, DateTime

class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)