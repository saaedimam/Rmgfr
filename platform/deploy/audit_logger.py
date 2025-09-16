from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import uuid

class AuditLogger:
    def __init__(self):
        self.audit_events = []
    
    def log_event(self, 
                  action: str, 
                  resource: str, 
                  user_id: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None):
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "resource": resource,
            "user_id": user_id,
            "details": details or {}
        }
        self.audit_events.append(event)
        return event["id"]
    
    def get_audit_trail(self, resource: Optional[str] = None, 
                       user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        events = self.audit_events
        
        if resource:
            events = [e for e in events if e["resource"] == resource]
        
        if user_id:
            events = [e for e in events if e["user_id"] == user_id]
        
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)

class StabilizeMode:
    def __init__(self):
        self.is_active = False
        self.rps_limit = 1000
        self.circuit_breaker_threshold = 0.1
    
    def activate(self, rps_limit: int = 1000):
        self.is_active = True
        self.rps_limit = rps_limit
        print("🛡️  Stabilize mode activated")
    
    def deactivate(self):
        self.is_active = False
        print("✅ Stabilize mode deactivated")
    
    def should_throttle(self, current_rps: float) -> bool:
        return self.is_active and current_rps > self.rps_limit
