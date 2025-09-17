"""
Events API router v2 - Real-time event processing with fraud detection
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid
import logging

from ..services.database import get_database, DatabaseService
from ..services.decision_gate import decision_gate, DecisionContext, Action
from ..services.fraud_engine import FraudEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v2/events", tags=["events"])

class EventCreate(BaseModel):
    event_type: str = Field(..., description="Type of event (login, signup, checkout, payment, custom)")
    event_data: dict = Field(default_factory=dict, description="Event-specific data")
    profile_id: Optional[str] = Field(None, description="External profile ID")
    session_id: Optional[str] = Field(None, description="Session identifier")
    device_fingerprint: Optional[str] = Field(None, description="Device fingerprint hash")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    amount: Optional[float] = Field(None, description="Transaction amount (for payment events)")
    currency: Optional[str] = Field(None, description="Currency code (for payment events)")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = ['login', 'signup', 'checkout', 'payment', 'custom']
        if v not in allowed_types:
            raise ValueError(f'event_type must be one of: {allowed_types}')
        return v

class EventResponse(BaseModel):
    id: str
    event_type: str
    event_data: dict
    profile_id: Optional[str]
    session_id: Optional[str]
    device_fingerprint: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    amount: Optional[float]
    currency: Optional[str]
    risk_score: Optional[float]
    decision: Optional[str]
    created_at: datetime

class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    page: int
    limit: int

class EventProcessingResult(BaseModel):
    event_id: str
    risk_score: float
    decision: str
    reasons: List[str]
    rules_fired: List[str]
    processing_time_ms: float

@router.post("/", response_model=EventProcessingResult, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    request: Request,
    db: DatabaseService = Depends(get_database)
):
    """
    Create a new event and process it through the fraud detection pipeline
    """
    start_time = datetime.now()
    
    try:
        # Extract project ID from API key (simplified for demo)
        project_id = "550e8400-e29b-41d4-a716-446655440001"  # Default test project
        
        # Generate event ID
        event_id = str(uuid.uuid4())
        
        # Extract IP address from request
        ip_address = event.ip_address or request.client.host if request.client else None
        
        # Calculate risk score using fraud engine
        fraud_engine = FraudEngine()
        risk_score = await fraud_engine.calculate_risk_score(
            event_type=event.event_type,
            event_data=event.event_data,
            profile_id=event.profile_id,
            device_fingerprint=event.device_fingerprint,
            ip_address=ip_address,
            amount=event.amount
        )
        
        # Get customer segment (simplified logic)
        customer_segment = "new_user" if event.event_type == "signup" else "returning"
        
        # Get latest FPR for this action type (simplified)
        latest_fpr = 0.01  # Default FPR
        
        # Make decision using decision gate
        decision_context = DecisionContext(
            event_type=event.event_type,
            risk_score=risk_score,
            customer_segment=customer_segment,
            latest_fpr=latest_fpr
        )
        
        action, confidence, reasons = decision_gate.decide(decision_context)
        
        # Store event in database
        event_data = {
            "id": event_id,
            "project_id": project_id,
            "event_type": event.event_type,
            "event_data": event.event_data,
            "profile_id": event.profile_id,
            "session_id": event.session_id,
            "device_fingerprint": event.device_fingerprint,
            "ip_address": ip_address,
            "user_agent": event.user_agent,
            "amount": event.amount,
            "currency": event.currency,
            "risk_score": risk_score,
            "decision": action.value,
            "created_at": datetime.now()
        }
        
        # Insert event
        insert_sql = """
        INSERT INTO events (
            id, project_id, event_type, event_data, profile_id, session_id,
            device_fingerprint, ip_address, user_agent, amount, currency,
            risk_score, decision, created_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
        )
        """
        
        await db.execute_command(
            insert_sql,
            event_id, project_id, event.event_type, event.event_data,
            event.profile_id, event.session_id, event.device_fingerprint,
            ip_address, event.user_agent, event.amount, event.currency,
            risk_score, action.value, datetime.now()
        )
        
        # Create decision record
        decision_id = str(uuid.uuid4())
        decision_sql = """
        INSERT INTO decisions (
            id, project_id, event_id, decision, risk_score, reasons, rules_fired, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        
        rules_fired = [f"risk_band_{decision_context.risk_score:.1f}", f"segment_{customer_segment}"]
        
        await db.execute_command(
            decision_sql,
            decision_id, project_id, event_id, action.value,
            risk_score, reasons, rules_fired, datetime.now()
        )
        
        # Create case if decision is review
        if action == Action.REVIEW:
            case_id = str(uuid.uuid4())
            case_sql = """
            INSERT INTO cases (id, project_id, decision_id, status, created_at)
            VALUES ($1, $2, $3, $4, $5)
            """
            await db.execute_command(
                case_sql,
                case_id, project_id, decision_id, "open", datetime.now()
            )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(f"Processed event {event_id}: {action.value} (risk: {risk_score:.3f})")
        
        return EventProcessingResult(
            event_id=event_id,
            risk_score=risk_score,
            decision=action.value,
            reasons=reasons,
            rules_fired=rules_fired,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Failed to process event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process event: {str(e)}"
        )

@router.get("/", response_model=EventListResponse)
async def list_events(
    project_id: str,
    page: int = 1,
    limit: int = 100,
    event_type: Optional[str] = None,
    decision: Optional[str] = None,
    db: DatabaseService = Depends(get_database)
):
    """
    List events for a project with filtering
    """
    try:
        # Build query
        where_conditions = ["project_id = $1"]
        params = [project_id]
        param_count = 1
        
        if event_type:
            param_count += 1
            where_conditions.append(f"event_type = ${param_count}")
            params.append(event_type)
        
        if decision:
            param_count += 1
            where_conditions.append(f"decision = ${param_count}")
            params.append(decision)
        
        where_clause = " AND ".join(where_conditions)
        
        # Get total count
        count_sql = f"SELECT COUNT(*) FROM events WHERE {where_clause}"
        total = await db.execute_one(count_sql, *params)
        total_count = total["count"] if total else 0
        
        # Get events with pagination
        offset = (page - 1) * limit
        events_sql = f"""
        SELECT id, event_type, event_data, profile_id, session_id, device_fingerprint,
               ip_address, user_agent, amount, currency, risk_score, decision, created_at
        FROM events 
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        
        params.extend([limit, offset])
        events = await db.execute_query(events_sql, *params)
        
        # Format response
        event_responses = [
            EventResponse(
                id=event["id"],
                event_type=event["event_type"],
                event_data=event["event_data"],
                profile_id=event["profile_id"],
                session_id=event["session_id"],
                device_fingerprint=event["device_fingerprint"],
                ip_address=event["ip_address"],
                user_agent=event["user_agent"],
                amount=event["amount"],
                currency=event["currency"],
                risk_score=float(event["risk_score"]) if event["risk_score"] else None,
                decision=event["decision"],
                created_at=event["created_at"]
            )
            for event in events
        ]
        
        return EventListResponse(
            events=event_responses,
            total=total_count,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to list events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list events: {str(e)}"
        )

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    project_id: str,
    db: DatabaseService = Depends(get_database)
):
    """
    Get a specific event by ID
    """
    try:
        event_sql = """
        SELECT id, event_type, event_data, profile_id, session_id, device_fingerprint,
               ip_address, user_agent, amount, currency, risk_score, decision, created_at
        FROM events 
        WHERE id = $1 AND project_id = $2
        """
        
        event = await db.execute_one(event_sql, event_id, project_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return EventResponse(
            id=event["id"],
            event_type=event["event_type"],
            event_data=event["event_data"],
            profile_id=event["profile_id"],
            session_id=event["session_id"],
            device_fingerprint=event["device_fingerprint"],
            ip_address=event["ip_address"],
            user_agent=event["user_agent"],
            amount=event["amount"],
            currency=event["currency"],
            risk_score=float(event["risk_score"]) if event["risk_score"] else None,
            decision=event["decision"],
            created_at=event["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event: {str(e)}"
        )

@router.get("/stats/summary")
async def get_event_stats(
    project_id: str,
    hours: int = 24,
    db: DatabaseService = Depends(get_database)
):
    """
    Get event statistics summary
    """
    try:
        stats_sql = """
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN decision = 'allow' THEN 1 END) as allowed_events,
            COUNT(CASE WHEN decision = 'deny' THEN 1 END) as denied_events,
            COUNT(CASE WHEN decision = 'review' THEN 1 END) as review_events,
            AVG(risk_score) as avg_risk_score,
            MAX(risk_score) as max_risk_score,
            MIN(risk_score) as min_risk_score
        FROM events 
        WHERE project_id = $1 
        AND created_at >= NOW() - INTERVAL '${hours} hours'
        """
        
        stats = await db.execute_one(stats_sql, project_id)
        
        if not stats:
            return {
                "total_events": 0,
                "allowed_events": 0,
                "denied_events": 0,
                "review_events": 0,
                "avg_risk_score": 0.0,
                "max_risk_score": 0.0,
                "min_risk_score": 0.0,
                "time_period_hours": hours
            }
        
        return {
            "total_events": stats["total_events"],
            "allowed_events": stats["allowed_events"],
            "denied_events": stats["denied_events"],
            "review_events": stats["review_events"],
            "avg_risk_score": float(stats["avg_risk_score"]) if stats["avg_risk_score"] else 0.0,
            "max_risk_score": float(stats["max_risk_score"]) if stats["max_risk_score"] else 0.0,
            "min_risk_score": float(stats["min_risk_score"]) if stats["min_risk_score"] else 0.0,
            "time_period_hours": hours
        }
        
    except Exception as e:
        logger.error(f"Failed to get event stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event stats: {str(e)}"
        )
