from pydantic import BaseModel, Field, EmailStr, model_validator, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime

class Employee(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="Unique row identifier for each user")
    emp_no: str = Field(..., max_length=10, description="Employee number")
    cn1: Optional[str] = Field(None, max_length=150, description="Full name or CN1 of the employee")
    email: Optional[EmailStr] = Field(None, description="Official email ID")
    sam_name: Optional[str] = Field(None, description="Unique identifier (SAM name)")
    division: Optional[str] = Field(None, max_length=100, description="Division within organization")
    business_unit: Optional[str] = Field(None, max_length=100, description="Business unit within organization")
    cost_center: Optional[str] = Field(None, max_length=50, description="Financial cost center code")
    cost_center_description: Optional[str] = Field(None, max_length=50, description="Descriptive name of cost center")
    physical_present: Optional[bool] = Field(default=True, description="Employee is physically present")
    legal_entities: Optional[str] = Field(None, max_length=100, description="Legal entity the user belongs to")
    location: Optional[str] = Field(None, max_length=100, description="Work location of user")
    joining_date: Optional[datetime] = Field(None, description="Joining date of employee")
    last_working_date: Optional[datetime] = Field(None, description="Last date of employee")
    created_at: Optional[datetime] = Field(None, description="Creation time")
    created_by: Optional[str] = Field(None, description="Creator name")
    modified_at: Optional[datetime] = Field(None, description="Last update time")
    modified_by: Optional[str] = Field(None, description="Modifier name")
    is_active: Optional[bool] = Field(default=True, description="Whether the employee is active")

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        if value and '@' not in value:
            raise ValueError('Invalid email format')
        return value.lower() if value else None

    @model_validator(mode='after')
    def check_joining_and_last_working_dates(self):
        if self.last_working_date and self.joining_date and self.joining_date > self.last_working_date:
            raise ValueError('joining_date cannot be after last_working_date')
        return self

class CreateEmployee(BaseModel):
    emp_no: str = Field(..., max_length=10, description="Employee number")
    cn1: Optional[str] = Field(None, max_length=150, description="Full name or CN1 of the employee")
    email: Optional[EmailStr] = Field(None, description="Official email ID")
    sam_name: Optional[str] = Field(None, description="Unique identifier (SAM name)")
    division: Optional[str] = Field(None, max_length=100, description="Division within organization")
    business_unit: Optional[str] = Field(None, max_length=100, description="Business unit within organization")
    cost_center: Optional[str] = Field(None, max_length=50, description="Financial cost center code")
    cost_center_description: Optional[str] = Field(None, max_length=50, description="Descriptive name of cost center")
    physical_present: Optional[bool] = Field(default=True, description="Employee is physically present")
    legal_entities: Optional[str] = Field(None, max_length=100, description="Legal entity the user belongs to")
    location: Optional[str] = Field(None, max_length=100, description="Work location of user")
    joining_date: Optional[datetime] = Field(None, description="Joining date of employee")
    last_working_date: Optional[datetime] = Field(None, description="Last date of employee")
    created_by: Optional[str] = Field(None, description="Creator name")
    is_active: Optional[bool] = Field(default=True, description="Whether the employee is active")
    modified_by: Optional[str] = Field(None, description="Modifier name")

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        if value and '@' not in value:
            raise ValueError('Invalid email format')
        return value.lower() if value else None

    @model_validator(mode='after')
    def check_joining_and_last_working_dates(self):
        if self.last_working_date and self.joining_date and self.joining_date > self.last_working_date:
            raise ValueError('joining_date cannot be after last_working_date')
        return self

class UpdateEmployee(BaseModel):
    emp_no: Optional[str] = Field(None, max_length=10, description="Employee number")
    cn1: Optional[str] = Field(None, max_length=150, description="Full name or CN1 of the employee")
    email: Optional[EmailStr] = Field(None, description="Official email ID")
    sam_name: Optional[str] = Field(None, description="Unique identifier (SAM name)")
    division: Optional[str] = Field(None, max_length=100, description="Division within organization")
    business_unit: Optional[str] = Field(None, max_length=100, description="Business unit within organization")
    cost_center: Optional[str] = Field(None, max_length=50, description="Financial cost center code")
    cost_center_description: Optional[str] = Field(None, max_length=50, description="Descriptive name of cost center")
    physical_present: Optional[bool] = Field(None, description="Employee is physically present")
    legal_entities: Optional[str] = Field(None, max_length=100, description="Legal entity the user belongs to")
    location: Optional[str] = Field(None, max_length=100, description="Work location of user")
    joining_date: Optional[datetime] = Field(None, description="Joining date of employee")
    last_working_date: Optional[datetime] = Field(None, description="Last date of employee")
    is_active: Optional[bool] = Field(None, description="Whether the employee is active")
    modified_by: Optional[str] = Field(None, description="Modifier name")

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        if value and '@' not in value:
            raise ValueError('Invalid email format')
        return value.lower() if value else None

    @model_validator(mode='after')
    def check_joining_and_last_working_dates(self):
        if self.last_working_date and self.joining_date and self.joining_date > self.last_working_date:
            raise ValueError('joining_date cannot be after last_working_date')
        return self

class PaginatedEmployeeResponse(BaseModel):
    data: List[Employee]
    total: int
    page: int
    page_size: int
    sort_by: Optional[str] = "id"
    order: Optional[str] = "asc"
    total_pages: int
