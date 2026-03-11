# routes/allocation_endpoints.py

from fastapi import APIRouter, HTTPException, Path, Depends, Query, status
from data_models.allocation_models import Allocation, UpdateAllocation, CreateAllocation, PaginatedAllocationResponse
from typing import List, Literal, Optional
from database.repositories.allocation_repository import AllocationRepository
from database.repositories.employee_repository import EmployeeRepository
from database.repositories.assets_repository import AssetRepository
from database.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/allocations",
    tags=["Allocations"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "",
    response_model=PaginatedAllocationResponse,
    summary="List allocations with pagination",
    description="Retrieve a paginated list of allocations with optional sorting."
)
async def list_allocations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Literal["id", "employee_id", "asset_id", "allotted_at", "returned_at"] = "id",
    order: Literal["asc", "desc"] = "asc",
    search: Optional[str] = Query(None, description="Search term (Employee name, number, or host name)"),
    db: AsyncSession = Depends(get_db)
):
    repo = AllocationRepository(db)
    skip = (page - 1) * page_size

    # Fetch data
    allocations = await repo.list_allocations(
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        order=order,
        search=search
    )

    total = await repo.count_allocations(search=search)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedAllocationResponse(
        data=allocations,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{allocation_id}",
    response_model=Allocation,
    summary="Get allocation by ID",
    description="Retrieve specific allocation details by their ID."
)
async def get_allocation(
    allocation_id: int = Path(..., description="ID of the allocation"),
    db: AsyncSession = Depends(get_db)
):  
    repo = AllocationRepository(db)
    allocation = await repo.get_allocation(allocation_id)
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Allocation with ID {allocation_id} not found"
        )
    return allocation


@router.post(
    "",
    response_model=Allocation,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new allocation",
    description="Create a new allocation record."
)
async def create_allocation(
    allocation_in: CreateAllocation,
    db: AsyncSession = Depends(get_db)
):
    # Resolve employee_id from emp_no
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_employee_by_emp_no(allocation_in.emp_no)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Employee with number {allocation_in.emp_no} not found"
        )
    
    # Resolve asset_id from host_name
    asset_repo = AssetRepository(db)
    asset = await asset_repo.get_asset_by_host_name(allocation_in.host_name)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Asset with host name {allocation_in.host_name} not found"
        )

    alloc_repo = AllocationRepository(db)
    # Check if asset is already allocated
    if await alloc_repo.is_asset_allocated(asset.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset '{allocation_in.host_name}' is already allocated."
        )

    try:
        allocation = await alloc_repo.add_allocation(
            employee_id=employee.id,
            asset_id=asset.id,
            allotted_at=allocation_in.allotted_at,
            returned_at=allocation_in.returned_at,
            remarks=allocation_in.remarks,
            created_by=allocation_in.created_by,
            modified_by=allocation_in.modified_by,
        )

        # Update Asset status and allocation flag
        await asset_repo.update_asset(
            asset.id,
            modified_by=allocation_in.modified_by or "System",
            is_allocated=True
        )
        allocation.emp_no = employee.emp_no
        allocation.host_name = asset.host_name
        return allocation
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{allocation_id}",
    response_model=Allocation,
    summary="Update an allocation",
    description="Update an existing allocation record."
)
async def update_allocation(
    allocation_id: int,
    allocation_update: UpdateAllocation,
    db: AsyncSession = Depends(get_db)
):
    repo = AllocationRepository(db)
    update_data = allocation_update.model_dump(exclude_unset=True)
    
    if not update_data:
        allocation = await repo.get_allocation(allocation_id)
        if not allocation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found")
        return allocation

    updated_allocation = await repo.update_allocation(allocation_id, **update_data)
    
    if not updated_allocation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found")
    
    return updated_allocation


@router.delete(
    "/{allocation_id}",
    summary="Delete an allocation",
    description="Remove an allocation record."
)
async def delete_allocation(
    allocation_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = AllocationRepository(db)
    # Get allocation first to find the asset
    allocation = await repo.get_allocation(allocation_id)
    if not allocation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found")
        
    asset_id = allocation.asset_id
    success = await repo.delete_allocation(allocation_id)
    
    if success:
        # Mark asset as Available again
        asset_repo = AssetRepository(db)
        await asset_repo.update_asset(asset_id, modified_by="System", is_allocated=False, status='Available')
        return {"status": "success", "message": f"Allocation {allocation_id} deleted and asset released"}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delete failed")
@router.get(
    "/asset/{asset_id}",
    response_model=List[Allocation],
    summary="Get allocation history for an asset",
    description="Retrieve the history of all employees who were assigned a specific asset."
)
async def get_asset_allocation_history(
    asset_id: int = Path(..., description="ID of the asset"),
    db: AsyncSession = Depends(get_db)
):
    repo = AllocationRepository(db)
    history = await repo.get_asset_history(asset_id)
    return history
