from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from database.models.db import AsyncSessionLocal
from database.repositories.assets_repository import AssetRepository
from database.repositories.employee_repository import EmployeeRepository

router = APIRouter()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/notifications/counts")
async def get_notification_counts(
    user_name: str = Query(..., description="Logged in user name"),
    db: AsyncSession = Depends(get_db)
):
    asset_repo = AssetRepository(db)
    emp_repo = EmployeeRepository(db)
    
    incomplete_assets = await asset_repo.count_incomplete_assets(user_name)
    incomplete_employees = await emp_repo.count_incomplete_employees(user_name)
    expired_warranties = await asset_repo.count_expired_warranty_assets()
    
    return {
        "incomplete_assets": incomplete_assets,
        "incomplete_employees": incomplete_employees,
        "expired_warranties": expired_warranties,
        "total": incomplete_assets + incomplete_employees + expired_warranties
    }

@router.get("/notifications/details")
async def get_notification_details(
    user_name: str = Query(..., description="Logged in user name"),
    db: AsyncSession = Depends(get_db)
):
    asset_repo = AssetRepository(db)
    emp_repo = EmployeeRepository(db)
    
    incomplete_assets_list = await asset_repo.get_incomplete_assets_uuids(user_name)
    incomplete_employees_list = await emp_repo.get_incomplete_employees_emp_nos(user_name)
    expired_warranty_hostnames = await asset_repo.get_expired_warranty_assets_hostnames()
    
    return {
        "incomplete_assets": incomplete_assets_list,
        "incomplete_employees": incomplete_employees_list,
        "expired_warranties": expired_warranty_hostnames
    }

