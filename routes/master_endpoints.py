from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.dependencies import get_db
from database.repositories.master_repository import MasterRepository
from data_models.master_models import (
    MasterKey, CreateMasterKey, UpdateMasterKey, PaginatedMasterKeyResponse,
    MasterValue, CreateMasterValue, UpdateMasterValue, PaginatedMasterValueResponse
)

router = APIRouter(prefix="/master", tags=["Master Data"])

# --- Master Key Endpoints ---

@router.post("/keys", response_model=MasterKey, status_code=status.HTTP_201_CREATED)
async def create_master_key(
    key_data: CreateMasterKey,
    db: AsyncSession = Depends(get_db)
):
    repo = MasterRepository(db)
    # Check if key exists? Handled by DB unique constraint or logic?
    # For now, let DB handle, but could be better to check first.
    try:
        new_key = await repo.create_key(
            key_name=key_data.key_name,
            is_active=key_data.is_active
        )
        return new_key
    except Exception as e:
        # Assuming duplicate key error handling or similar
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/keys", response_model=PaginatedMasterKeyResponse)
async def list_master_keys(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = "id",
    order: str = "asc",
    db: AsyncSession = Depends(get_db)
):
    repo = MasterRepository(db)
    skip = (page - 1) * page_size
    keys = await repo.list_keys(skip=skip, limit=page_size, sort_by=sort_by, order=order)
    total = await repo.count_keys()
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "data": keys,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("/keys/{key_id}", response_model=MasterKey)
async def get_master_key(key_id: int, db: AsyncSession = Depends(get_db)):
    repo = MasterRepository(db)
    key = await repo.get_key(key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Master Key not found")
    return key

@router.put("/keys/{key_id}", response_model=MasterKey)
async def update_master_key(
    key_id: int,
    key_update: UpdateMasterKey,
    db: AsyncSession = Depends(get_db)
):
    repo = MasterRepository(db)
    updated_key = await repo.update_key(key_id, **key_update.model_dump(exclude_unset=True))
    if not updated_key:
        raise HTTPException(status_code=404, detail="Master Key not found")
    return updated_key

@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_master_key(key_id: int, db: AsyncSession = Depends(get_db)):
    repo = MasterRepository(db)
    success = await repo.delete_key(key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Master Key not found")
    return None

# --- Master Value Endpoints ---

@router.post("/values", response_model=MasterValue, status_code=status.HTTP_201_CREATED)
async def create_master_value(
    value_data: CreateMasterValue,
    db: AsyncSession = Depends(get_db)
):
    repo = MasterRepository(db)
    # Validate key_id exists? 
    key = await repo.get_key(value_data.key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Master Key not found")
        
    try:
        new_val = await repo.create_value(
            key_id=value_data.key_id,
            value=value_data.value,
            order_id=value_data.order_id,
            is_active=value_data.is_active
        )
        return new_val
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/values", response_model=PaginatedMasterValueResponse)
async def list_master_values(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = "id",
    order: str = "asc",
    key_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    repo = MasterRepository(db)
    skip = (page - 1) * page_size
    values = await repo.list_values(skip=skip, limit=page_size, sort_by=sort_by, order=order, key_id=key_id)
    total = await repo.count_values(key_id=key_id)
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "data": values,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("/values/{value_id}", response_model=MasterValue)
async def get_master_value(value_id: int, db: AsyncSession = Depends(get_db)):
    repo = MasterRepository(db)
    val = await repo.get_value(value_id)
    if not val:
        raise HTTPException(status_code=404, detail="Master Value not found")
    return val

@router.put("/values/{value_id}", response_model=MasterValue)
async def update_master_value(
    value_id: int,
    value_update: UpdateMasterValue,
    db: AsyncSession = Depends(get_db)
):
    repo = MasterRepository(db)
    updated_val = await repo.update_value(value_id, **value_update.model_dump(exclude_unset=True))
    if not updated_val:
        raise HTTPException(status_code=404, detail="Master Value not found")
    return updated_val

@router.delete("/values/{value_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_master_value(value_id: int, db: AsyncSession = Depends(get_db)):
    repo = MasterRepository(db)
    success = await repo.delete_value(value_id)
    if not success:
        raise HTTPException(status_code=404, detail="Master Value not found")
    return None
