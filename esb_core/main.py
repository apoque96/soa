from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from .router import MessageRouter

app = FastAPI(title="ESB Core")
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

    print("Received message for routing:", message)
    
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