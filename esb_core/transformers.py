from typing import Dict, Any

class MessageTransformer:
    """Transform messages between different service formats"""
    
    @staticmethod
    def membership_to_user_validation_format(membership_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform membership data to user validation format"""
        return {
            "user_id": membership_data.get("user_id")
        }
    
    @staticmethod
    def passthrough(data: Dict[str, Any]) -> Dict[str, Any]:
        """Pass data through without transformation"""
        return data
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> tuple[bool, str]:
        """Validate message structure"""
        required_fields = ["source", "destination", "message_type", "payload"]
        
        for field in required_fields:
            if field not in message:
                return False, f"Missing required field: {field}"
        
        return True, "Valid"
    
    @staticmethod
    def enrich_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata to message"""
        from datetime import datetime
        
        message["esb_timestamp"] = datetime.now().isoformat()
        message["esb_version"] = "1.0"
        return message