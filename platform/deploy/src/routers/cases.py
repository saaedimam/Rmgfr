"""
Cases API router for fraud case management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

from ..models.database import get_db, Case, Decision, Project

router = APIRouter(prefix="/v1/cases", tags=["cases"])

class CaseResponse(BaseModel):
    id: str
    decision_id: str
    status: str
    assigned_to: Optional[str]
    resolution: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class CaseListResponse(BaseModel):
    cases: List[CaseResponse]
    total: int
    page: int
    limit: int

class CaseUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Case status: open, reviewed, closed")
    assigned_to: Optional[str] = Field(None, description="User assigned to case")
    resolution: Optional[str] = Field(None, description="Case resolution: approved, rejected, escalated")
    notes: Optional[str] = Field(None, description="Case notes")
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['open', 'reviewed', 'closed']
            if v not in allowed_statuses:
                raise ValueError(f'status must be one of: {allowed_statuses}')
        return v
    
    @validator('resolution')
    def validate_resolution(cls, v):
        if v is not None:
            allowed_resolutions = ['approved', 'rejected', 'escalated']
            if v not in allowed_resolutions:
                raise ValueError(f'resolution must be one of: {allowed_resolutions}')
        return v

@router.get("/", response_model=CaseListResponse)
async def list_cases(
    project_id: str,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List fraud cases for a project with pagination"""
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
        
        # Build query
        query = select(Case).where(Case.project_id == project_id)
        
        if status:
            query = query.where(Case.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Case.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        cases = result.scalars().all()
        
        # Format response
        case_responses = [
            CaseResponse(
                id=str(case.id),
                decision_id=str(case.decision_id),
                status=case.status,
                assigned_to=case.assigned_to,
                resolution=case.resolution,
                notes=case.notes,
                created_at=case.created_at,
                updated_at=case.updated_at
            )
            for case in cases
        ]
        
        return CaseListResponse(
            cases=case_responses,
            total=total,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list cases: {str(e)}"
        )

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific case by ID"""
    try:
        result = await db.execute(
            select(Case).where(
                and_(
                    Case.id == case_id,
                    Case.project_id == project_id
                )
            )
        )
        case = result.scalar_one_or_none()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        return CaseResponse(
            id=str(case.id),
            decision_id=str(case.decision_id),
            status=case.status,
            assigned_to=case.assigned_to,
            resolution=case.resolution,
            notes=case.notes,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get case: {str(e)}"
        )

@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    project_id: str,
    case_update: CaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a fraud case"""
    try:
        # Get case
        result = await db.execute(
            select(Case).where(
                and_(
                    Case.id == case_id,
                    Case.project_id == project_id
                )
            )
        )
        case = result.scalar_one_or_none()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        # Update fields
        if case_update.status is not None:
            case.status = case_update.status
        if case_update.assigned_to is not None:
            case.assigned_to = case_update.assigned_to
        if case_update.resolution is not None:
            case.resolution = case_update.resolution
        if case_update.notes is not None:
            case.notes = case_update.notes
        
        # Update timestamp
        case.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(case)
        
        return CaseResponse(
            id=str(case.id),
            decision_id=str(case.decision_id),
            status=case.status,
            assigned_to=case.assigned_to,
            resolution=case.resolution,
            notes=case.notes,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update case: {str(e)}"
        )

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    decision_id: str,
    project_id: str,
    assigned_to: Optional[str] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a new fraud case for manual review"""
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
        
        # Validate decision exists
        decision_result = await db.execute(
            select(Decision).where(
                and_(
                    Decision.id == decision_id,
                    Decision.project_id == project_id
                )
            )
        )
        decision = decision_result.scalar_one_or_none()
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found"
            )
        
        # Create case
        case = Case(
            project_id=project_id,
            decision_id=decision_id,
            assigned_to=assigned_to,
            notes=notes
        )
        
        db.add(case)
        await db.commit()
        await db.refresh(case)
        
        return CaseResponse(
            id=str(case.id),
            decision_id=str(case.decision_id),
            status=case.status,
            assigned_to=case.assigned_to,
            resolution=case.resolution,
            notes=case.notes,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create case: {str(e)}"
        )
