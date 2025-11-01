from datetime import datetime
from pydantic import BaseModel, field_serializer
from typing import Dict, Any, List, Optional

# Base Response Model
class BaseResponse(BaseModel):
    status: str
    message: Optional[str] = None

# Base Request Models
class BaseRequest(BaseModel):
    pass

# ESB Core Models
class ESBMessage(BaseModel):
    source: str
    destination: str
    message_type: str
    payload: Dict[str, Any]

class ESBRoutingResult(BaseResponse):
    result: Optional[Dict[str, Any]] = None

class ESBHistoryEntry(BaseModel):
    message: Dict[str, Any]
    result: Dict[str, Any]

class ESBHistory(BaseModel):
    total_messages: int
    recent_messages: List[ESBHistoryEntry]

class ESBHealth(BaseModel):
    service: str
    status: str
    messages_processed: int

class ESBServices(BaseModel):
    services: Dict[str, str]
    routing_rules: Dict[str, Dict[str, Any]]

# User Service Models
class UserBase(BaseModel):
    name: str
    email: str
    status: str
    phone: str

class UserCreate(UserBase, BaseRequest):
    pass

class User(UserBase):
    user_id: int
    registration_date: datetime

    @field_serializer('registration_date')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()

class UserResponse(BaseResponse):
    data: Optional[User] = None

class UsersListResponse(BaseResponse):
    data: Optional[List[User]] = None
    total: Optional[int] = None

# Membership Service Models
class MembershipBase(BaseModel):
    user_id: int
    plan_type: str
    payment_status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    benefits: Optional[str] = None


class MembershipCreate(MembershipBase, BaseRequest):
    pass

class Membership(BaseModel):
    membership_id: int
    user_id: int
    plan_type: str
    payment_status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    benefits: Optional[str] = None

    @field_serializer('start_date', 'end_date')
    def serialize_datetime(self, dt: datetime | None, _info):
        if dt is None:
            return None
        return dt.isoformat()

class MembershipResponse(BaseResponse):
    data: Optional[Membership] = None

class MembershipsListResponse(BaseResponse):
    data: Optional[List[Membership]] = None
    total: Optional[int] = None

# Service Catalog Models
class ServiceBase(BaseModel):
    name: str
    description: str

class ServiceCreate(ServiceBase, BaseRequest):
    pass

class Service(ServiceBase):
    service_id: int

class ServiceResponse(BaseResponse):
    data: Optional[Service] = None

class ServicesListResponse(BaseResponse):
    data: Optional[List[Service]] = None
    skip: int
    limit: int
    total: Optional[int] = None

# Provider Service Models
class ProviderBase(BaseModel):
    name: str
    email: str
    services: str

class ProviderCreate(ProviderBase, BaseRequest):
    pass

class Provider(ProviderBase):
    provider_id: int

class ProviderResponse(BaseResponse):
    data: Optional[Provider] = None

class ProvidersListResponse(BaseResponse):
    data: Optional[List[Provider]] = None
    skip: int
    limit: int
    total: Optional[int] = None