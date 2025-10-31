import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str
    status: str
    phone: str
    registration_date: datetime.datetime = datetime.datetime.now()

class User(UserBase):
    user_id: int

    class Config:
        from_attributes = True

class UserValidateRequest(BaseModel):
    user_id: int