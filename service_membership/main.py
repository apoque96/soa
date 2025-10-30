from fastapi import FastAPI, HTTPException, Depends
from . import db, models, services, schemas
from .db import get_db, engine
from sqlalchemy.orm import Session
from typing import List
import httpx

app = FastAPI(title="Membership Service")

@app.get("/membership/health")
async def health():
    return {
        "service": "membership-service",
        "status": "healthy"
    }

@app.get("/memberships/", response_model=List[schemas.Membership])
def read_memberships(db: Session = Depends(get_db)):
    return services.get_memberships(db)

@app.get("/memberships/{membership_id}", response_model=schemas.Membership)
def read_membership(membership_id: int, db: Session = Depends(get_db)):
    membership = services.get_membership_by_id(db, membership_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership

@app.post("/memberships/", response_model=schemas.Membership)
async def create_membership(membership: schemas.MembershipBase, db: Session = Depends(get_db)):
    """Create a new membership - sends to ESB for user validation"""
    try:
        # Convert membership to dict with serialized datetime
        membership_dict = membership.model_dump()
        
        # Convert datetime objects to ISO format strings
        if isinstance(membership_dict.get('start_date'), str) is False:
            membership_dict['start_date'] = membership_dict['start_date'].isoformat() if membership_dict.get('start_date') else None
        if isinstance(membership_dict.get('end_date'), str) is False:
            membership_dict['end_date'] = membership_dict['end_date'].isoformat() if membership_dict.get('end_date') else None
        
        esb_url = "http://esb:8001/esb/route"
        payload = {
            "source": "membership-service",
            "destination": "user-service",
            "message_type": "membership.create",
            "payload": membership_dict
        }
        
        print(f"Attempting to connect to ESB at: {esb_url}")
        print(f"Payload: {payload}")
        
        # Send to ESB for validation and processing
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(esb_url, json=payload)
                print(f"ESB Response Status: {response.status_code}")
                print(f"ESB Response Body: {response.text}")
                response.raise_for_status()
                result = response.json()
            except httpx.ConnectError as ce:
                print(f"Connection Error: {ce}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Cannot connect to ESB at {esb_url}. Is it running on port 8001?"
                )
            except httpx.TimeoutException as te:
                print(f"Timeout Error: {te}")
                raise HTTPException(
                    status_code=504,
                    detail="ESB request timed out"
                )
            response.raise_for_status()
            result = response.json()
        
        # If ESB validation passed, create the membership
        if result.get("status") == "success":
            return services.create_membership(db, membership)
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get("message", "Failed to validate membership")
            )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"ESB validation failed: {e.response.json()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating membership: {str(e)}")

@app.post("/memberships/internal/create", response_model=schemas.Membership)
async def create_membership_internal(membership: schemas.MembershipBase, db: Session = Depends(get_db)):
    """Internal endpoint for ESB to create membership after validation"""
    try:
        print(f"Internal create received: {membership.model_dump()}")
        return services.create_membership(db, membership)
    except Exception as e:
        print(f"Error in internal create: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))