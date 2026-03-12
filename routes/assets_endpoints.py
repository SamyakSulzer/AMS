from fastapi import APIRouter, HTTPException, Path, Depends, UploadFile, File, Query
from data_models.asset_models import Asset, UpdateAsset, CreateAsset, PaginatedAssetResponse, AssetSummaryResponse
from typing import List, AsyncGenerator, Literal, Optional
import pandas as pd
import io
from database.repositories.assets_repository import AssetRepository
from database.models.db import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

router = APIRouter()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session



@router.get("/asset_page", response_model=PaginatedAssetResponse)
async def get_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: Literal["asset_type", "location", "is_allocated", "status", "model", "host_name", "id", "serial_num", "staging_status", "company_name", "u_uid"] = "id",
    order: Literal["asc", "desc"] = "asc",
    search: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    repo = AssetRepository(db)
    skip = (page - 1) * page_size

    # 1. Get the actual data
    assets = await repo.list_assets(
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        order=order,
        search=search,
        asset_type=asset_type
    )

    total = await repo.count_assets(search=search, asset_type=asset_type)

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedAssetResponse(
        data=assets,
        total=total,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        total_pages=total_pages
    )

@router.get("/asset", response_model=List[Asset])
async def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=5000),
    sort_by: Literal["asset_type", "location", "is_allocated", "status", "model", "host_name", "id", "serial_num", "staging_status", "company_name"] = "id",
    order: Literal["asc", "desc"] = "asc",
    db: AsyncSession = Depends(get_db)
):
    repo = AssetRepository(db)
    assets = await repo.list_assets(skip=skip, limit=limit, sort_by=sort_by, order=order)
    return assets

@router.get("/assets/summary", response_model=List[AssetSummaryResponse])
async def get_asset_summary(db: AsyncSession = Depends(get_db)):
    repo = AssetRepository(db)
    return await repo.get_asset_summary_by_category()

@router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(
    asset_id: int = Path(..., examples=1, description="ID of the asset"),
    db: AsyncSession = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = await repo.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/assets", response_model=Asset)
async def create_asset(A: CreateAsset, db: AsyncSession = Depends(get_db)):
    repo = AssetRepository(db)

    asset = await repo.add_asset(
        asset_type=A.asset_type,
        serial_num=A.serial_num,
        host_name=A.host_name,
        make=A.make,
        model=A.model,
        lifecycle_status=A.lifecycle_status,
        purchase_date=A.purchase_date,
        warranty_start_date=A.warranty_start_date,
        warranty_end_date=A.warranty_end_date,
        last_issued=A.last_issued,
        u_uid=A.u_uid,
        mac_id=A.mac_id,
        company_name=A.company_name,
        location=A.location,
        created_by=A.created_by,
        modified_by=A.modified_by,
        remarks=A.remarks,
        is_allocated=A.is_allocated,
        is_deleted=A.is_deleted,
        staging_status=A.staging_status,
        status=A.status,
    )
    return asset


@router.put("/assets/{asset_id}", response_model=dict)
async def update_asset(
    asset_id: int,
    U: UpdateAsset,
    db: AsyncSession = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = await repo.get_asset(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    update_data = U.model_dump(exclude_unset=True)
    modified_by = update_data.pop("modified_by", U.modified_by or asset.modified_by)
    asset = await repo.update_asset(asset_id, modified_by, **update_data)

    return {"status": "updated", "id": asset_id}


@router.delete("/assets/{asset_id}", response_model=dict)
async def delete_asset(
    asset_id: int = Path(..., description="ID of the asset"),
    db: AsyncSession = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = await repo.get_asset(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    await repo.delete_asset(asset_id)
    return {"status": "deleted", "id": asset_id}


@router.post("/upload_assets_csv")
async def upload_assets_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        repo = AssetRepository(db)
        added_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Sanitize row: replace NaN with None, ensure proper types, and strip spaces from headers
                row_dict = {k.strip(): (v if pd.notnull(v) else None) for k, v in row.items()}
                
                # Backward compatibility: Map common UUID header variations to 'u_uid'
                uuid_variations = ['UUID', 'U_UID', 'U_uid', 'u_uid']
                if not row_dict.get('u_uid'):
                    for var in uuid_variations:
                        if var in row_dict and row_dict[var]:
                            row_dict['u_uid'] = row_dict[var]
                            break
                
                # Force string conversion for fields that Pydantic expects as strings
                string_fields = [
                    'asset_type', 'host_name', 'make', 'model', 
                    'lifecycle_status', 'mac_id', 'company_name', 
                    'location', 'serial_num', 'remarks', 'u_uid', 'staging_status', 'status'
                ]
                for field in string_fields:
                    if field in row_dict and row_dict[field] is not None:
                        row_dict[field] = str(row_dict[field])

                # Convert date columns to date objects if they exist
                for d_field in ['purchase_date', 'warranty_start_date', 'warranty_end_date']:
                    if row_dict.get(d_field):
                        try:
                            row_dict[d_field] = pd.to_datetime(row_dict[d_field]).date()
                        except:
                            row_dict[d_field] = None
                
                # Convert datetime columns if they exist
                if row_dict.get('last_issued'):
                    try:
                        row_dict['last_issued'] = pd.to_datetime(row_dict['last_issued']).to_pydatetime()
                    except:
                        row_dict['last_issued'] = None
                
                # Handle boolean fields
                bool_fields = ['is_allocated', 'is_deleted']
                for field in bool_fields:
                    if field in row_dict and row_dict[field] is not None:
                        if isinstance(row_dict[field], str):
                            row_dict[field] = row_dict[field].lower() in ('true', '1', 'yes')

                # Normalize staging_status and status values
                if row_dict.get('staging_status'):
                    ss = str(row_dict['staging_status']).lower().replace('_', ' ')
                    if ss == 'not staged' or ss == 'not_staged':
                        row_dict['staging_status'] = 'Not Staged'
                    elif ss == 'staged':
                        row_dict['staging_status'] = 'Staged'
                
                if row_dict.get('status'):
                    st = str(row_dict['status']).lower().replace('-', ' ')
                    if st == 'in stock' or st == 'in-stock':
                        row_dict['status'] = 'In-Stock'
                    elif st == 'allocated':
                        row_dict['status'] = 'Allocated'
                    elif st == 'retired':
                        row_dict['status'] = 'Retired'
                    elif st == 'available': # Handle legacy 'Available' -> 'In-Stock'
                        row_dict['status'] = 'In-Stock'
                
                # Use the existing CreateAsset model for validation
                asset_data = CreateAsset(**row_dict)
                
                await repo.add_asset(
                    asset_type=asset_data.asset_type,
                    serial_num=asset_data.serial_num,
                    host_name=asset_data.host_name,
                    make=asset_data.make,
                    model=asset_data.model,
                    lifecycle_status=asset_data.lifecycle_status,
                    purchase_date=asset_data.purchase_date,
                    warranty_start_date=asset_data.warranty_start_date,
                    warranty_end_date=asset_data.warranty_end_date,
                    last_issued=asset_data.last_issued,
                    u_uid=asset_data.u_uid,
                    mac_id=asset_data.mac_id,
                    company_name=asset_data.company_name,
                    location=asset_data.location,
                    created_by=asset_data.created_by,
                    modified_by=asset_data.modified_by,
                    remarks=asset_data.remarks,
                    is_allocated=asset_data.is_allocated,
                    is_deleted=asset_data.is_deleted,
                    staging_status=asset_data.staging_status,
                    status=asset_data.status
                )
                added_count += 1
            except Exception as e:
                errors.append({"row": index + 2, "error": str(e)}) # +2 for header and 1-index offset
                continue
                
        return {
            "status": "completed", 
            "added_count": added_count, 
            "failed_count": len(errors),
            "errors": errors[:10]  # Return first 10 errors for feedback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
