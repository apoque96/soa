import datetime
from .db import Base
from sqlalchemy import Column, Integer, String, DateTime

class Provider(Base):
    __tablename__ = "providers"

    provider_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    services = Column(String, index=True)