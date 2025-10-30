from typing import Dict, Any
import httpx
from .transformers import MessageTransformer

class MessageRouter:
    """Route messages to appropriate destinations"""
    
    # Service registry - maps service names to endpoints
    SERVICE_REGISTRY = {
        "user-service": "http://users_service:8002/users/validate",
        "membership-service": "http://membership_service:8004/memberships/internal/create"
    }
    
    # Routing rules - maps message types to transformations and destinations
    ROUTING_RULES = {
        "membership.create": {
            "destination_service": "user-service",
            "transformer": "membership_to_user_validation_format",
            "validation_required": True,
            "callback_service": "membership-service"
        }
    }
    
    def __init__(self):
        self.transformer = MessageTransformer()
    
    async def route_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Route message based on type and destination"""
        
        # Validate message
        is_valid, validation_msg = self.transformer.validate_message(message)
        if not is_valid:
            return {
                "status": "error",
                "message": validation_msg
            }
        
        # Enrich message with metadata
        message = self.transformer.enrich_message(message)
        
        # Get routing rule
        message_type = message.get("message_type")
        routing_rule = self.ROUTING_RULES.get(message_type)
        
        if not routing_rule:
            return {
                "status": "error",
                "message": f"No routing rule found for message type: {message_type}"
            }
        
        # Check if validation is required
        if routing_rule.get("validation_required"):
            return await self._route_with_validation(message, routing_rule)
        else:
            return await self._route_simple(message, routing_rule)
    
    async def _route_simple(self, message: Dict[str, Any], routing_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Simple routing without validation"""
        # Transform message
        transformed_payload = self._transform_payload(
            message["payload"],
            routing_rule["transformer"]
        )
        
        # Get destination endpoint
        destination_service = routing_rule["destination_service"]
        endpoint = self.SERVICE_REGISTRY.get(destination_service)
        
        if not endpoint:
            return {
                "status": "error",
                "message": f"Service not found: {destination_service}"
            }
        
        # Send to destination
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(endpoint, json=transformed_payload)
                response.raise_for_status()
                
                return {
                    "status": "success",
                    "message": "Message routed successfully",
                    "destination": destination_service,
                    "response": response.json()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to route message: {str(e)}",
                "destination": destination_service
            }
    
    async def _route_with_validation(self, message: Dict[str, Any], routing_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Route with validation step (e.g., check user exists before creating membership)"""
        
        # Step 1: Validate (e.g., check if user exists)
        validation_payload = self._transform_payload(
            message["payload"],
            routing_rule["transformer"]
        )
        
        validation_service = routing_rule["destination_service"]
        validation_endpoint = self.SERVICE_REGISTRY.get(validation_service)
        
        if not validation_endpoint:
            return {
                "status": "error",
                "message": f"Validation service not found: {validation_service}"
            }
        
        try:
            # Call validation endpoint
            async with httpx.AsyncClient(timeout=10.0) as client:
                validation_response = await client.post(
                    validation_endpoint,
                    json=validation_payload
                )
                validation_response.raise_for_status()
                validation_result = validation_response.json()
            
            # Check validation result
            if not validation_result.get("valid", False):
                return {
                    "status": "error",
                    "message": f"Validation failed: {validation_result.get('message', 'Unknown error')}",
                    "validation_service": validation_service
                }
            
            # Step 2: If validation passed, call the callback service
            callback_service = routing_rule.get("callback_service")
            if callback_service:
                callback_endpoint = self.SERVICE_REGISTRY.get(callback_service)
                
                if not callback_endpoint:
                    return {
                        "status": "error",
                        "message": f"Callback service not found: {callback_service}"
                    }
                
                # Send original payload to callback service
                async with httpx.AsyncClient(timeout=10.0) as client:
                    callback_response = await client.post(
                        callback_endpoint,
                        json=message["payload"]
                    )
                    callback_response.raise_for_status()
                    
                    return {
                        "status": "success",
                        "message": "Validation passed and membership created",
                        "validation": validation_result,
                        "result": callback_response.json()
                    }
            
            # If no callback, just return validation success
            return {
                "status": "success",
                "message": "Validation passed",
                "validation": validation_result
            }
            
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "message": f"HTTP error during routing: {str(e)}",
                "details": e.response.text if hasattr(e, 'response') else None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to route message: {str(e)}"
            }
    
    def _transform_payload(self, payload: Dict[str, Any], transformer_name: str) -> Dict[str, Any]:
        """Apply transformation to payload"""
        transformer_method = getattr(self.transformer, transformer_name, None)
        if transformer_method:
            return transformer_method(payload)
        return payload