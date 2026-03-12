from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict
from typing import List, Optional, Literal
from datetime import date, datetime

class CreateAsset(BaseModel):
    asset_type: str = Field(..., max_length=50, description="Type of asset")
    serial_num: str = Field(..., max_length=100, description="Serial number of device")
    host_name: Optional[str] = Field(None, max_length=100, description="Stores system/host name")
    make: Optional[str] = Field(None, max_length=100, description="Manufacturer of the asset")
    model: Optional[str] = Field(None, max_length=120, description="Model name")
    lifecycle_status: str = Field(..., max_length=30, description="Cycle stage")
    purchase_date: date = Field(..., description="Date on which asset was purchased")
    warranty_start_date: Optional[date] = Field(None, description="Warranty start date")
    warranty_end_date: Optional[date] = Field(None, description="Warranty expiry date")
    last_issued: Optional[datetime] = Field(None, description="Last issued timestamp")
    u_uid: str = Field(..., max_length=50, description="Unique identifier for the asset")
    mac_id: Optional[str] = Field(None, max_length=30, description="Mac address of the asset")
    company_name: Optional[str] = Field(None, max_length=100, description="Company that owns the asset")
    location: Optional[str] = Field(None, max_length=50, description="Physical location of the asset")
    created_by: Optional[str] = Field(None, description="Creator user name")
    modified_by: Optional[str] = Field(None, description="Modifier user name")
    remarks: Optional[str] = Field(None, max_length=500, description="Additional remarks")
    is_allocated: bool = Field(default=False, description="Asset is Allocated")
    is_deleted: bool = Field(default=False, description="Asset is deleted")
    staging_status: Optional[Literal["Not Staged", "Staged"]] = Field('Not Staged', description="Staging status")
    status: Optional[Literal["In-Stock", "Allocated", "Retired"]] = Field('In-Stock', description="Current status of the asset")

    @field_validator('make')
    @classmethod
    def make_validator(cls, value):
        if value:
            valid_makers = ['LENOVO', 'HP', 'SAMSUNG', 'DELL', 'APPLE']
            asset = value.upper()
            if asset not in valid_makers:
                return value # Allow others but normalize if in list? No, let's just return as is if not in list for now or keep validation.
            return asset
        return value

    @model_validator(mode='after')
    def check_warranty_dates(self):
        if self.warranty_end_date and self.purchase_date and self.warranty_end_date < self.purchase_date:
            raise ValueError('warranty_end_date cannot be earlier than purchase_date')
        return self

class Asset(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="Unique row identifier for each asset")
    asset_type: str = Field(..., max_length=50, description="Type of asset")
    serial_num: str = Field(..., max_length=100, description="Serial number of device")
    host_name: Optional[str] = Field(None, max_length=100, description="Stores system/host name")
    make: Optional[str] = Field(None, max_length=100, description="Manufacturer of the asset")
    model: Optional[str] = Field(None, max_length=120, description="Model name")
    lifecycle_status: str = Field(..., max_length=30, description="Cycle stage")
    purchase_date: date = Field(..., description="Date on which asset was purchased")
    warranty_start_date: Optional[date] = Field(None, description="Warranty start date")
    warranty_end_date: Optional[date] = Field(None, description="Warranty expiry date")
    last_issued: Optional[datetime] = Field(None, description="Last issued timestamp")
    u_uid: str = Field(..., max_length=50, description="Unique identifier for the asset")
    mac_id: Optional[str] = Field(None, max_length=30, description="Mac address of the asset")
    company_name: Optional[str] = Field(None, max_length=100, description="Company that owns the asset")
    location: Optional[str] = Field(None, max_length=50, description="Physical location of the asset")
    created_at: datetime = Field(..., description="Creation time")
    created_by: str = Field(..., description="Creator user name")
    modified_at: datetime = Field(..., description="Last update time")
    modified_by: str = Field(..., description="Modifier user name")
    remarks: Optional[str] = Field(None, max_length=500, description="Additional remarks")
    is_allocated: bool = Field(..., description="Asset is allocated")
    is_deleted: bool = Field(..., description="Asset is deleted")
    staging_status: Optional[Literal["Not Staged", "Staged"]] = Field(None, description="Staging status")
    status: Optional[Literal["In-Stock", "Allocated", "Retired"]] = Field(None, description="Current status of the asset")

class UpdateAsset(BaseModel):
    asset_type: Optional[str] = Field(None, max_length=50, description="Type of asset")
    serial_num: Optional[str] = Field(None, max_length=100, description="Serial number of device")
    host_name: Optional[str] = Field(None, max_length=100, description="Stores system/host name")
    make: Optional[str] = Field(None, max_length=100, description="Manufacturer of the asset")
    model: Optional[str] = Field(None, max_length=120, description="Model name")
    lifecycle_status: Optional[str] = Field(None, max_length=30, description="Cycle stage")
    purchase_date: Optional[date] = Field(None, description="Date on which asset was purchased")
    warranty_start_date: Optional[date] = Field(None, description="Warranty start date")
    warranty_end_date: Optional[date] = Field(None, description="Warranty expiry date")
    last_issued: Optional[datetime] = Field(None, description="Last issued timestamp")
    u_uid: Optional[str] = Field(None, max_length=50, description="Unique identifier for the asset")
    mac_id: Optional[str] = Field(None, max_length=30, description="Mac address of the asset")
    company_name: Optional[str] = Field(None, max_length=100, description="Company that owns the asset")
    location: Optional[str] = Field(None, max_length=50, description="Physical location of the asset")
    remarks: Optional[str] = Field(None, max_length=500, description="Additional remarks")
    is_allocated: Optional[bool] = Field(None, description="Asset is Allocated")
    is_deleted: Optional[bool] = Field(None, description="Asset is deleted")
    modified_by: Optional[str] = Field(None, description="Modifier user name")
    staging_status: Optional[Literal["Not Staged", "Staged"]] = Field(None, description="Staging status")
    status: Optional[Literal["In-Stock", "Allocated", "Retired"]] = Field(None, description="Current status of the asset")

class PaginatedAssetResponse(BaseModel):
    data: List[Asset]
    total: int
    page: int
    page_size: int
    sort_by: Optional[str] = "id"
    order: Optional[str] = "asc"
    total_pages: int
class AssetSummaryResponse(BaseModel):
    category: str
    in_stock: int
    allocated: int
    retired: int
    total: int
    consumption: float
