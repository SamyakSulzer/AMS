# routes/emp_endpoints.py

from fastapi import APIRouter, HTTPException, Path, Depends, UploadFile, File, Query, status
from data_models.employee_models import Employee, UpdateEmployee, CreateEmployee, PaginatedEmployeeResponse
from typing import List, Literal, Optional
from datetime import datetime
import pandas as pd
import io
from database.repositories.employee_repository import EmployeeRepository
from database.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=PaginatedEmployeeResponse,
    summary="List employees with pagination",
    description="Retrieve a paginated list of employees with optional sorting and filtering."
)
async def list_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Literal["cn1", "business_unit", "division", "location", "physical_present", "id", "is_active", "emp_no"] = "id",
    order: Literal["asc", "desc"] = "asc",
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of employees.
    
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 20)
    - **sort_by**: Field to sort by
    - **order**: Sort order (asc/desc)
    - **search**: Search query
    - **status**: "ACTIVE", "INACTIVE", or "All"
    """
    repo = EmployeeRepository(db)
    skip = (page - 1) * page_size

    is_active = None
    if status == "ACTIVE":
        is_active = True
    elif status == "INACTIVE":
        is_active = False

    # Fetch data
    employees = await repo.list_employees(
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        order=order,
        search=search,
        is_active=is_active
    )

    total = await repo.count_employees(search=search, is_active=is_active)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedEmployeeResponse(
        data=employees,
        total=total,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        total_pages=total_pages
    )


@router.get(
    "/{employee_id}",
    response_model=Employee,
    summary="Get employee by ID",
    description="Retrieve specific employee details by their ID."
)
async def get_employee(
    employee_id: int = Path(..., examples=[1], description="ID of the employee"),
    db: AsyncSession = Depends(get_db)
):  
    repo = EmployeeRepository(db)
    employee = await repo.get_employee(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Employee with ID {employee_id} not found"
        )
    return employee


@router.post(
    "",
    response_model=Employee,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
    description="Create a new employee record."
)
async def create_employee(
    employee_in: CreateEmployee,
    db: AsyncSession = Depends(get_db)
):
    repo = EmployeeRepository(db)
    
    # Check if logic for duplicates is needed (e.g. email or sam_name uniqueness), 
    # relying on database constraints for now which will raise IntegrityError if violated.
    # Ideally, one might check existence first to return 409 Conflict.
    try:
        employee = await repo.add_employee(
            emp_no=employee_in.emp_no,
            cn1=employee_in.cn1,
            email=employee_in.email,
            sam_name=employee_in.sam_name,
            division=employee_in.division,
            business_unit=employee_in.business_unit,
            cost_center=employee_in.cost_center,
            cost_center_description=employee_in.cost_center_description,
            physical_present=employee_in.physical_present,
            legal_entities=employee_in.legal_entities,
            location=employee_in.location,
            joining_date=employee_in.joining_date,
            last_working_date=employee_in.last_working_date,
            created_by=employee_in.created_by,
            modified_by=employee_in.modified_by,
            is_active=employee_in.is_active,
        )
        return employee
    except Exception as e:
        # In a real app, catch specific IntegrityError for duplicates
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{employee_id}",
    response_model=Employee,
    summary="Update an employee",
    description="Update an existing employee record."
)
async def update_employee(
    employee_id: int,
    employee_update: UpdateEmployee,
    db: AsyncSession = Depends(get_db)
):
    repo = EmployeeRepository(db)
    
    # Use model_dump to get dict, excluding unset fields
    update_data = employee_update.model_dump(exclude_unset=True)
    
    if not update_data:
        # No fields to update
        employee = await repo.get_employee(employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return employee

    updated_employee = await repo.update_employee(employee_id, **update_data)
    
    if not updated_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    return updated_employee


@router.delete(
    "/{employee_id}",
    summary="Delete an employee",
    description="Soft delete or remove an employee."
)
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = EmployeeRepository(db)
    employee = await repo.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    await repo.delete_employee(employee_id)
    return {"status": "success", "message": f"Employee {employee_id} deleted successfully"}


@router.post(
    "/upload-csv",
    summary="Bulk upload employees via CSV",
    description="Upload a CSV file containing employee records."
)
async def upload_employees_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are allowed")
    
    try:
        content = await file.read()
        # Use pandas to read CSV
        df = pd.read_csv(io.BytesIO(content))
        
        # Replace NaN with None
        df = df.where(pd.notnull(df), None)
        
        repo = EmployeeRepository(db)
        added_count = 0
        errors = []
        
        # Fields that must be strings
        string_fields = ['cost_center', 'legal_entities', 'sam_name', 'emp_no',
                         'cost_center_description', 'division', 'location', 'cn1', 'business_unit']
        
        records = df.to_dict('records')
        
        for index, row in enumerate(records):
            try:
                # 1. Sanitize row
                row_dict = {k.strip(): (v if pd.notnull(v) else None) for k, v in row.items()}
                
                # 2. Type casting for string fields
                for field in string_fields:
                    if field in row_dict and row_dict[field] is not None:
                        row_dict[field] = str(row_dict[field])

                # 3. Date conversion
                for date_field in ['joining_date', 'last_working_date']:
                    if row_dict.get(date_field):
                        row_dict[date_field] = pd.to_datetime(row_dict[date_field]).to_pydatetime()
                
                # 4. Validate using Pydantic Model
                employee_data = CreateEmployee(**row_dict)
                
                # 5. Add to DB
                await repo.add_employee(
                    emp_no=employee_data.emp_no,
                    cn1=employee_data.cn1,
                    email=employee_data.email,
                    sam_name=employee_data.sam_name,
                    division=employee_data.division,
                    business_unit=employee_data.business_unit,
                    cost_center=employee_data.cost_center,
                    cost_center_description=employee_data.cost_center_description,
                    legal_entities=employee_data.legal_entities,
                    location=employee_data.location,
                    joining_date=employee_data.joining_date,
                    last_working_date=employee_data.last_working_date,
                    created_by=employee_data.created_by,
                    modified_by=employee_data.modified_by,
                    is_active=employee_data.is_active,
                    physical_present=employee_data.physical_present
                )
                added_count += 1
            except Exception as e:
                # Capture row number (index + 2 for header + 0-index) and error
                errors.append({"row": index + 2, "error": str(e)})
                continue
                
        return {
            "status": "completed", 
            "added_count": added_count, 
            "failed_count": len(errors),
            "errors": errors[:10]  # Return top 10 errors
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV: {str(e)}"
        )