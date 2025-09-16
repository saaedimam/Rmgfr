from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class Incident:
    id: str
    title: str
    severity: str  # critical, high, medium, low
    status: str    # open, investigating, resolved
    created_at: datetime
    resolved_at: datetime = None
    timeline: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timeline is None:
            self.timeline = []

class IncidentManager:
    def __init__(self):
        self.incidents: List[Incident] = []
    
    def create_incident(self, title: str, severity: str) -> Incident:
        incident = Incident(
            id=f"INC-{len(self.incidents) + 1:04d}",
            title=title,
            severity=severity,
            status="open",
            created_at=datetime.utcnow()
        )
        self.incidents.append(incident)
        return incident
    
    def add_timeline_event(self, incident_id: str, event: str, details: str = ""):
        incident = next((i for i in self.incidents if i.id == incident_id), None)
        if incident:
            incident.timeline.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": event,
                "details": details
            })
    
    def resolve_incident(self, incident_id: str):
        incident = next((i for i in self.incidents if i.id == incident_id), None)
        if incident:
            incident.status = "resolved"
            incident.resolved_at = datetime.utcnow()
            self.add_timeline_event(incident_id, "Incident resolved")
