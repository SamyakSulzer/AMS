from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import date, datetime

class Allocation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    asset_id: int
    emp_no: Optional[str] = None
    employee_name: Optional[str] = None
    host_name: Optional[str] = None
    asset_type: Optional[str] = None
    allotted_at: datetime
    returned_at: Optional[datetime] = None
    remarks: Optional[str] = None
    created_at: datetime
    created_by: Optional[str] = None
    modified_at: datetime
    modified_by: Optional[str] = None

class CreateAllocation(BaseModel):
    emp_no: str
    host_name: str
    allotted_at: datetime = Field(default_factory=datetime.utcnow)
    returned_at: Optional[datetime] = None
    remarks: Optional[str] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

class UpdateAllocation(BaseModel):
    employee_id: Optional[int] = None
    asset_id: Optional[int] = None
    allotted_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    remarks: Optional[str] = None
    modified_by: Optional[str] = None

class PaginatedAllocationResponse(BaseModel):
    data: List[Allocation]
    total: int
    page: int
    page_size: int
    total_pages: int
