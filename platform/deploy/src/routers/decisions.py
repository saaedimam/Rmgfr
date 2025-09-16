"""
Decisions API router for fraud decision management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

from ..models.database import get_db, Decision, Event, Profile, Project
from ..services.fraud_engine import FraudEngine

router = APIRouter(prefix="/v1/decisions", tags=["decisions"])

class DecisionCreate(BaseModel):
    event_id: Optional[str] = Field(None, description="Event ID to evaluate")
    profile_id: Optional[str] = Field(None, description="Profile ID to evaluate")
    decision: str = Field(..., description="Decision: allow, deny, or review")
    risk_score: Optional[float] = Field(None, ge=0, le=1, description="Risk score 0-1")
    reasons: List[str] = Field(default_factory=list, description="Decision reasons")
    rules_fired: List[str] = Field(default_factory=list, description="Rules that fired")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    
    @validator('decision')
    def validate_decision(cls, v):
        allowed_decisions = ['allow', 'deny', 'review']
        if v not in allowed_decisions:
            raise ValueError(f'decision must be one of: {allowed_decisions}')
        return v

class DecisionResponse(BaseModel):
    id: str
    event_id: Optional[str]
    profile_id: Optional[str]
    decision: str
    risk_score: Optional[float]
    reasons: List[str]
    rules_fired: List[str]
    metadata: dict
    created_at: datetime

class DecisionListResponse(BaseModel):
    decisions: List[DecisionResponse]
    total: int
    page: int
    limit: int

@router.post("/", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(
    decision: DecisionCreate,
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Create a new fraud decision"""
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
        
        # Validate event exists if provided
        event_uuid = None
        if decision.event_id:
            event_result = await db.execute(
                select(Event).where(
                    and_(
                        Event.id == decision.event_id,
                        Event.project_id == project_id
                    )
                )
            )
            event = event_result.scalar_one_or_none()
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found"
                )
            event_uuid = event.id
        
        # Validate profile exists if provided
        profile_uuid = None
        if decision.profile_id:
            profile_result = await db.execute(
                select(Profile).where(
                    and_(
                        Profile.project_id == project_id,
                        Profile.external_id == decision.profile_id
                    )
                )
            )
            profile = profile_result.scalar_one_or_none()
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )
            profile_uuid = profile.id
        
        # Create decision
        decision_record = Decision(
            project_id=project_id,
            event_id=event_uuid,
            profile_id=profile_uuid,
            decision=decision.decision,
            risk_score=decision.risk_score,
            reasons=decision.reasons,
            rules_fired=decision.rules_fired,
            metadata=decision.metadata
        )
        
        db.add(decision_record)
        await db.commit()
        await db.refresh(decision_record)
        
        return DecisionResponse(
            id=str(decision_record.id),
            event_id=decision.event_id,
            profile_id=decision.profile_id,
            decision=decision_record.decision,
            risk_score=decision_record.risk_score,
            reasons=decision_record.reasons,
            rules_fired=decision_record.rules_fired,
            metadata=decision_record.metadata,
            created_at=decision_record.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create decision: {str(e)}"
        )

@router.get("/", response_model=DecisionListResponse)
async def list_decisions(
    project_id: str,
    page: int = 1,
    limit: int = 100,
    decision: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List decisions for a project with pagination"""
    try:
        # Build query
        query = select(Decision).where(Decision.project_id == project_id)
        
        if decision:
            query = query.where(Decision.decision == decision)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Decision.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        decisions = result.scalars().all()
        
        # Format response
        decision_responses = [
            DecisionResponse(
                id=str(decision.id),
                event_id=str(decision.event_id) if decision.event_id else None,
                profile_id=str(decision.profile_id) if decision.profile_id else None,
                decision=decision.decision,
                risk_score=float(decision.risk_score) if decision.risk_score else None,
                reasons=decision.reasons,
                rules_fired=decision.rules_fired,
                metadata=decision.metadata,
                created_at=decision.created_at
            )
            for decision in decisions
        ]
        
        return DecisionListResponse(
            decisions=decision_responses,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list decisions: {str(e)}"
        )

@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: str,
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific decision by ID"""
    try:
        result = await db.execute(
            select(Decision).where(
                and_(
                    Decision.id == decision_id,
                    Decision.project_id == project_id
                )
            )
        )
        decision = result.scalar_one_or_none()
        
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found"
            )
        
        return DecisionResponse(
            id=str(decision.id),
            event_id=str(decision.event_id) if decision.event_id else None,
            profile_id=str(decision.profile_id) if decision.profile_id else None,
            decision=decision.decision,
            risk_score=float(decision.risk_score) if decision.risk_score else None,
            reasons=decision.reasons,
            rules_fired=decision.rules_fired,
            metadata=decision.metadata,
            created_at=decision.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get decision: {str(e)}"
        )
