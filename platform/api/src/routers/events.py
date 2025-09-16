"""
Events API router for transaction event ingestion
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

from ..models.database import get_db, Event, Profile, Project
from ..services.fraud_engine import FraudEngine

router = APIRouter(prefix="/v1/events", tags=["events"])

class EventCreate(BaseModel):
    event_type: str = Field(..., description="Type of event (login, signup, checkout, custom)")
    event_data: dict = Field(default_factory=dict, description="Event-specific data")
    profile_id: Optional[str] = Field(None, description="External profile ID")
    session_id: Optional[str] = Field(None, description="Session identifier")
    device_fingerprint: Optional[str] = Field(None, description="Device fingerprint hash")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = ['login', 'signup', 'checkout', 'custom']
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
    created_at: datetime

class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    page: int
    limit: int

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Create a new transaction event"""
    try:
        # Validate project exists
        project_result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get or create profile if profile_id provided
        profile_uuid = None
        if event.profile_id:
            profile_result = await db.execute(
                select(Profile).where(
                    and_(
                        Profile.project_id == project_id,
                        Profile.external_id == event.profile_id
                    )
                )
            )
            profile = profile_result.scalar_one_or_none()
            if not profile:
                # Create new profile
                profile = Profile(
                    project_id=project_id,
                    external_id=event.profile_id,
                    device_fingerprint=event.device_fingerprint
                )
                db.add(profile)
                await db.flush()
            profile_uuid = profile.id
        
        # Create event
        event_record = Event(
            project_id=project_id,
            profile_id=profile_uuid,
            event_type=event.event_type,
            event_data=event.event_data,
            device_fingerprint=event.device_fingerprint,
            session_id=event.session_id
        )
        
        db.add(event_record)
        await db.commit()
        await db.refresh(event_record)
        
        return EventResponse(
            id=str(event_record.id),
            event_type=event_record.event_type,
            event_data=event_record.event_data,
            profile_id=event.profile_id,
            session_id=event_record.session_id,
            device_fingerprint=event_record.device_fingerprint,
            created_at=event_record.created_at
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )

@router.get("/", response_model=EventListResponse)
async def list_events(
    project_id: str,
    page: int = 1,
    limit: int = 100,
    event_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List events for a project with pagination"""
    try:
        # Build query
        query = select(Event).where(Event.project_id == project_id)
        
        if event_type:
            query = query.where(Event.event_type == event_type)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Event.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        events = result.scalars().all()
        
        # Format response
        event_responses = [
            EventResponse(
                id=str(event.id),
                event_type=event.event_type,
                event_data=event.event_data,
                profile_id=event.profile_id,
                session_id=event.session_id,
                device_fingerprint=event.device_fingerprint,
                created_at=event.created_at
            )
            for event in events
        ]
        
        return EventListResponse(
            events=event_responses,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list events: {str(e)}"
        )

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific event by ID"""
    try:
        result = await db.execute(
            select(Event).where(
                and_(
                    Event.id == event_id,
                    Event.project_id == project_id
                )
            )
        )
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return EventResponse(
            id=str(event.id),
            event_type=event.event_type,
            event_data=event.event_data,
            profile_id=event.profile_id,
            session_id=event.session_id,
            device_fingerprint=event.device_fingerprint,
            created_at=event.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event: {str(e)}"
        )
