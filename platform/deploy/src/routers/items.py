"""
Items CRUD endpoints
"""

from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.database import DatabaseService
from ..services.redis import RedisService


router = APIRouter()


class ItemCreate(BaseModel):
    """Item creation model"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: str = Field(default="pending", regex="^(pending|approved|rejected)$")


class ItemUpdate(BaseModel):
    """Item update model"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, regex="^(pending|approved|rejected)$")


class Item(BaseModel):
    """Item response model"""
    id: UUID
    title: str
    description: Optional[str]
    status: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[Item])
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(pending|approved|rejected)$"),
    db: DatabaseService = Depends(),
    redis: RedisService = Depends()
) -> List[Item]:
    """
    Get items with pagination and filtering
    
    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        status: Filter by status
        db: Database service
        redis: Redis service
    
    Returns:
        List[Item]: List of items
    """
    # TODO: Add authentication to get actual user_id
    user_id = "demo-user-id"
    
    # Build query
    query = """
        SELECT id, title, description, status, owner_id, created_at, updated_at
        FROM items
        WHERE owner_id = $1
    """
    params = [user_id]
    
    if status:
        query += " AND status = $2"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT $3 OFFSET $4"
    params.extend([limit, skip])
    
    try:
        rows = await db.fetch_all(query, params)
        return [Item(**row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch items: {str(e)}")


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: UUID,
    db: DatabaseService = Depends(),
    redis: RedisService = Depends()
) -> Item:
    """
    Get a specific item by ID
    
    Args:
        item_id: Item UUID
        db: Database service
        redis: Redis service
    
    Returns:
        Item: The requested item
    """
    # TODO: Add authentication to get actual user_id
    user_id = "demo-user-id"
    
    query = """
        SELECT id, title, description, status, owner_id, created_at, updated_at
        FROM items
        WHERE id = $1 AND owner_id = $2
    """
    
    try:
        row = await db.fetch_one(query, [item_id, user_id])
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return Item(**row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch item: {str(e)}")


@router.post("/", response_model=Item)
async def create_item(
    item: ItemCreate,
    db: DatabaseService = Depends(),
    redis: RedisService = Depends()
) -> Item:
    """
    Create a new item
    
    Args:
        item: Item creation data
        db: Database service
        redis: Redis service
    
    Returns:
        Item: The created item
    """
    # TODO: Add authentication to get actual user_id
    user_id = "demo-user-id"
    
    item_id = uuid4()
    now = datetime.utcnow()
    
    query = """
        INSERT INTO items (id, title, description, status, owner_id, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, title, description, status, owner_id, created_at, updated_at
    """
    
    try:
        row = await db.fetch_one(query, [
            item_id,
            item.title,
            item.description,
            item.status,
            user_id,
            now,
            now
        ])
        
        # Invalidate cache
        await redis.delete(f"user_items:{user_id}")
        
        return Item(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create item: {str(e)}")


@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: UUID,
    item_update: ItemUpdate,
    db: DatabaseService = Depends(),
    redis: RedisService = Depends()
) -> Item:
    """
    Update an existing item
    
    Args:
        item_id: Item UUID
        item_update: Item update data
        db: Database service
        redis: Redis service
    
    Returns:
        Item: The updated item
    """
    # TODO: Add authentication to get actual user_id
    user_id = "demo-user-id"
    
    # Build dynamic update query
    update_fields = []
    params = []
    param_count = 1
    
    if item_update.title is not None:
        update_fields.append(f"title = ${param_count}")
        params.append(item_update.title)
        param_count += 1
    
    if item_update.description is not None:
        update_fields.append(f"description = ${param_count}")
        params.append(item_update.description)
        param_count += 1
    
    if item_update.status is not None:
        update_fields.append(f"status = ${param_count}")
        params.append(item_update.status)
        param_count += 1
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append(f"updated_at = ${param_count}")
    params.append(datetime.utcnow())
    param_count += 1
    
    # Add WHERE clause parameters
    params.extend([item_id, user_id])
    
    query = f"""
        UPDATE items
        SET {', '.join(update_fields)}
        WHERE id = ${param_count} AND owner_id = ${param_count + 1}
        RETURNING id, title, description, status, owner_id, created_at, updated_at
    """
    
    try:
        row = await db.fetch_one(query, params)
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Invalidate cache
        await redis.delete(f"user_items:{user_id}")
        await redis.delete(f"item:{item_id}")
        
        return Item(**row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")


@router.delete("/{item_id}")
async def delete_item(
    item_id: UUID,
    db: DatabaseService = Depends(),
    redis: RedisService = Depends()
) -> dict:
    """
    Delete an item
    
    Args:
        item_id: Item UUID
        db: Database service
        redis: Redis service
    
    Returns:
        dict: Success message
    """
    # TODO: Add authentication to get actual user_id
    user_id = "demo-user-id"
    
    query = "DELETE FROM items WHERE id = $1 AND owner_id = $2"
    
    try:
        result = await db.execute(query, [item_id, user_id])
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Invalidate cache
        await redis.delete(f"user_items:{user_id}")
        await redis.delete(f"item:{item_id}")
        
        return {"message": "Item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete item: {str(e)}")
