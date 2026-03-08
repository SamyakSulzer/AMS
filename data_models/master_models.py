from pydantic import BaseModel, Field
from typing import List, Optional

# --- MasterKey Schemas ---

class CreateMasterKey(BaseModel):
    key_name: str = Field(..., max_length=100, description="Full name of the master key")
    is_active: bool = Field(default=True, description="Whether Key is active")
    is_deleted: bool = Field(default=False, description="Soft delete flag")

class UpdateMasterKey(BaseModel):
    key_name: Optional[str] = Field(None, max_length=100, description="Full name of the master key")
    is_active: Optional[bool] = Field(None, description="Whether Key is active")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")

class MasterKey(BaseModel):
    id: int = Field(..., description="Unique row identifier for each master key")
    key_name: str = Field(..., max_length=100, description="Full name of the master key")
    is_active: bool = Field(..., description="Whether Key is active")
    is_deleted: bool = Field(..., description="Soft delete flag")

# --- MasterValue Schemas ---

class CreateMasterValue(BaseModel):
    key_id: int = Field(..., description="Foreign key to MasterKey")
    value: List[str] = Field(..., description="Actual value")
    order_id: Optional[int] = Field(None, description="Order value")
    is_active: bool = Field(default=True, description="Active status")
    is_deleted: bool = Field(default=False, description="Soft delete flag")

class UpdateMasterValue(BaseModel):
    key_id: Optional[int] = Field(None, description="Foreign key to MasterKey")
    value: Optional[List[str]] = Field(None, description="Actual value (replaces entire list)")
    append_value: Optional[str] = Field(None, description="String to add to the existing list")
    remove_value: Optional[str] = Field(None, description="String to remove from the existing list")
    order_id: Optional[int] = Field(None, description="Order value")
    is_active: Optional[bool] = Field(None, description="Active status")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")

class MasterValue(BaseModel):
    id: int = Field(..., description="Unique identifier")
    key_id: int = Field(..., description="Foreign key to MasterKey")
    value: List[str] = Field(..., description="Actual value")
    order_id: Optional[int] = Field(None, description="Order value")
    is_active: bool = Field(..., description="Active status")
    is_deleted: bool = Field(..., description="Soft delete flag")

# --- Paginated Responses ---

class PaginatedMasterKeyResponse(BaseModel):
    data: List[MasterKey]
    total: int
    page: int
    page_size: int
    total_pages: int

class PaginatedMasterValueResponse(BaseModel):
    data: List[MasterValue]
    total: int
    page: int
    page_size: int
    total_pages: int
