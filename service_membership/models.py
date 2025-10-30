import datetime
from .db import Base
from sqlalchemy import Column, Integer, String, DateTime

class Membership(Base):
    __tablename__ = "memberships"

    membership_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    plan_type = Column(String, index=True)
    payment_status = Column(String, default="active")
    start_date = Column(DateTime, default=datetime.datetime.now)
    end_date = Column(DateTime, nullable=True)