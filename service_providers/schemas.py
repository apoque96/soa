from pydantic import BaseModel

class ProviderBase(BaseModel):
    name: str
    email: str
    services: str

class ProviderCreate(ProviderBase):
    pass

class Provider(ProviderBase):
    provider_id: int

    class Config:
        from_attributes = True