import datetime
from pydantic import BaseModel, field_serializer
from typing import Optional

class MembershipBase(BaseModel):
    user_id: int
    plan_type: str
    payment_status: str
    start_date: Optional[str] = None  # Accept as string in ISO format
    end_date: Optional[str] = None
    benefits: Optional[str] = None

class Membership(BaseModel):
    membership_id: int
    user_id: int
    plan_type: str
    payment_status: str
    start_date: datetime.datetime  # Database returns datetime
    end_date: Optional[datetime.datetime] = None
    benefits: Optional[str] = None
    
    # Serialize datetime to ISO format string for JSON response
    @field_serializer('start_date', 'end_date')
    def serialize_datetime(self, dt: datetime.datetime | None, _info):
        if dt is None:
            return None
        return dt.isoformat()
    
    class Config:
        from_attributes = True