from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import httpx
from .router import MessageRouter
from .schemas import (
    ESBMessage, ESBRoutingResult, ESBHealth, ESBHistory, ESBServices,
    UserCreate, UserResponse, UsersListResponse,
    MembershipCreate, MembershipResponse, MembershipsListResponse,
    ServiceCreate, ServiceResponse, ServicesListResponse,
    ProviderCreate, ProviderResponse, ProvidersListResponse
)

app = FastAPI(title="ESB Core")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = MessageRouter()

# Store message history for monitoring
message_history = []

@app.post("/esb/route", response_model=ESBRoutingResult)
async def route_message(message: ESBMessage):
    """Main ESB routing endpoint"""
    
    message_dict = message.model_dump()
    
    # Route the message
    result = await router.route_message(message_dict)
    
    # Store in history
    message_history.append({
        "message": message_dict,
        "result": result
    })
    
    # Keep only last 100 messages
    if len(message_history) > 100:
        message_history.pop(0)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    
    return ESBRoutingResult(status="success", result=result)

# Frontend-friendly endpoints
@app.post("/api/users", response_model=UserResponse)
async def create_user_via_esb(user_data: UserCreate):
    """Frontend endpoint to create a user"""
    result = await router.route_message({
        "source": "frontend",
        "destination": "user-service",
        "message_type": "user.create",
        "payload": user_data.model_dump()
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    # Extract user object from downstream response
    user = result.get("response")
    return UserResponse(status="success", data=user)

@app.get("/api/users", response_model=UsersListResponse)
async def get_users_via_esb():
    """Frontend endpoint to get all users"""
    result = await router.route_message({
        "source": "frontend",
        "destination": "user-service",
        "message_type": "user.list",
        "payload": {}
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    # Extract user list from downstream response
    users = result.get("response")
    return UsersListResponse(status="success", data=users)

@app.post("/api/memberships", response_model=MembershipResponse)
async def create_membership_via_esb(membership_data: MembershipCreate):
    """Frontend endpoint to create a membership"""
    result = await router.route_message({
        "source": "frontend",
        "destination": "user-service",
        "message_type": "membership.create",
        "payload": membership_data.model_dump(mode="json")
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    membership = result.get("response")

    return MembershipResponse(status="success", data=membership)

@app.get("/api/memberships", response_model=MembershipsListResponse)
async def get_memberships_via_esb():
    """Frontend endpoint to get all memberships"""
    result = await router.route_message({
        "source": "frontend",
        "destination": "membership-service",
        "message_type": "membership.list",
        "payload": {}
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    memberships = result.get("response")
    return MembershipsListResponse(status="success", data=memberships)


# Proxy endpoints to new catalog and provider services
@app.get("/api/services/", response_model=ServicesListResponse)
async def list_services(skip: int = 0, limit: int = 100):
    """Proxy: list services from catalog service"""
    url = f"http://catalog_service:8006/services/?skip={skip}&limit={limit}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return ServicesListResponse(
                    status="success",
                    data=data,
                    skip=skip,
                    limit=limit,
                    total=len(data)
                )
            return ServicesListResponse(
                status="success",
                data=data.get("items", data),
                skip=skip,
                limit=limit,
                total=data.get("total", len(data.get("items", data)))
            )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int):
    """Proxy: get a single service by id from catalog service"""
    url = f"http://catalog_service:8006/services/{service_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return ServiceResponse(status="success", data=resp.json())
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/services/", response_model=ServiceResponse)
async def create_service(service_data: ServiceCreate):
    """Proxy: create a service in catalog service"""
    url = "http://catalog_service:8006/services/"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=service_data.model_dump())
            resp.raise_for_status()
            return ServiceResponse(status="success", data=resp.json())
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/providers/", response_model=ProvidersListResponse)
async def list_providers(skip: int = 0, limit: int = 100):
    """Proxy: list providers from provider service"""
    url = f"http://providers_service:8005/providers/?skip={skip}&limit={limit}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return ProvidersListResponse(
                    status="success",
                    data=data,
                    skip=skip,
                    limit=limit,
                    total=len(data)
                )
            return ProvidersListResponse(
                status="success",
                data=data.get("items", data),
                skip=skip,
                limit=limit,
                total=data.get("total", len(data.get("items", data)))
            )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: int):
    """Proxy: get a single provider by id from provider service"""
    url = f"http://providers_service:8005/providers/{provider_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return ProviderResponse(status="success", data=resp.json())
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/providers/", response_model=ProviderResponse)
async def create_provider(provider_data: ProviderCreate):
    """Proxy: create a provider in provider service"""
    url = "http://providers_service:8005/providers/"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=provider_data.model_dump())
            resp.raise_for_status()
            return ProviderResponse(status="success", data=resp.json())
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/esb/health", response_model=ESBHealth)
async def health():
    return ESBHealth(
        service="esb-core",
        status="healthy",
        messages_processed=len(message_history)
    )

@app.get("/esb/history", response_model=ESBHistory)
async def get_message_history(limit: int = 10):
    """Get recent message history"""
    return ESBHistory(
        total_messages=len(message_history),
        recent_messages=message_history[-limit:]
    )

@app.get("/esb/services", response_model=ESBServices)
async def list_services():
    """List registered services"""
    return ESBServices(
        services=router.SERVICE_REGISTRY,
        routing_rules=router.ROUTING_RULES
    )