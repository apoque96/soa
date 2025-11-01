from pydantic import BaseModel

class ServiceBase(BaseModel):
    name: str
    description: str

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    service_id: int

    class Config:
        from_attributes = True