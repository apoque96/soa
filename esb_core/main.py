from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from .router import MessageRouter

app = FastAPI(title="ESB Core")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = MessageRouter()

class ESBMessage(BaseModel):
    source: str
    destination: str
    message_type: str
    payload: Dict[str, Any]

# Store message history for monitoring
message_history = []

@app.post("/esb/route")
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
    
    return result

# Frontend-friendly endpoints
@app.post("/api/users")
async def create_user_via_esb(user_data: Dict[str, Any]):
    """Frontend endpoint to create a user"""
    result = await router.route_message({
        "source": "frontend",
        "destination": "user-service",
        "message_type": "user.create",
        "payload": user_data
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.get("/api/users")
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
    
    return result

@app.post("/api/memberships")
async def create_membership_via_esb(membership_data: Dict[str, Any]):
    """Frontend endpoint to create a membership"""
    result = await router.route_message({
        "source": "frontend",
        "destination": "user-service",
        "message_type": "membership.create",
        "payload": membership_data
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.get("/api/memberships")
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
    
    return result

@app.get("/esb/health")
async def health():
    return {
        "service": "esb-core",
        "status": "healthy",
        "messages_processed": len(message_history)
    }

@app.get("/esb/history")
async def get_message_history(limit: int = 10):
    """Get recent message history"""
    return {
        "total_messages": len(message_history),
        "recent_messages": message_history[-limit:]
    }

@app.get("/esb/services")
async def list_services():
    """List registered services"""
    return {
        "services": router.SERVICE_REGISTRY,
        "routing_rules": router.ROUTING_RULES
    }