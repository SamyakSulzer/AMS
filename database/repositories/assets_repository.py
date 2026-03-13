# database/repositories/asset_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, String
from datetime import datetime, timezone
from database.mappers.assets_map import Asset
from sqlalchemy import select, func

from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError
from datetime import datetime, timezone




class AssetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def count_assets(self, search: str | None = None, asset_type: str | None = None) -> int:
        from sqlalchemy import or_
        query = select(func.count()).select_from(Asset)
        
        if asset_type and asset_type != "All":
            query = query.where(Asset.asset_type == asset_type)
            
        if search:
            search_filter = or_(
                Asset.host_name.ilike(f"%{search}%"),
                Asset.model.ilike(f"%{search}%"),
                Asset.make.ilike(f"%{search}%"),
                Asset.company_name.ilike(f"%{search}%"),
                Asset.serial_num.ilike(f"%{search}%"),
                Asset.location.ilike(f"%{search}%"),
                Asset.mac_id.ilike(f"%{search}%"),
                Asset.status.ilike(f"%{search}%"),
                Asset.u_uid.ilike(f"%{search}%"),
                func.cast(Asset.assetno, String).ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            
        result = await self.session.execute(query)
        return result.scalar() or 0 

    
    async def add_asset(
        self,
        assetno: int,
        asset_type: str,
        serial_num: str,
        lifecycle_status: str,
        purchase_date,
        u_uid: str,
        created_by: str | None = None,
        modified_by: str | None = None,
        host_name: str | None = None,
        make: str | None = None,
        model: str | None = None,
        warranty_start_date = None,
        warranty_end_date = None,
        last_issued = None,
        mac_id: str | None = None,
        company_name: str | None = None,
        location: str | None = None,
        remarks: str | None = None,
        is_allocated: bool = False,
        is_deleted: bool = False,
        staging_status: str | None = 'Not Staged',
        status: str | None = 'In-Stock',
    ) -> "Asset":
        now = datetime.now(timezone.utc)
        asset = Asset(
            assetno=assetno,
            asset_type=asset_type,
            serial_num=serial_num,
            host_name=host_name,
            make=make,
            model=model,
            lifecycle_status=lifecycle_status,
            purchase_date=purchase_date,
            warranty_start_date=warranty_start_date,
            warranty_end_date=warranty_end_date,
            last_issued=last_issued,
            u_uid=u_uid,
            mac_id=mac_id,
            company_name=company_name,
            location=location,
            created_at=now,
            created_by=created_by,
            modified_at=now,
            modified_by=modified_by,
            remarks=remarks,
            is_allocated=is_allocated,
            is_deleted=is_deleted,
            staging_status=staging_status,
            status=status,
        )

        try:
            self.session.add(asset)
            # This will attempt the INSERT; any constraint violations will surface here.
            await self.session.commit()
            await self.session.refresh(asset)
            return asset

        except (IntegrityError, DataError, OperationalError, ProgrammingError) as e:
            # IMPORTANT: reset the session so next rows can continue
            await self.session.rollback()
            # Optional: re-raise or wrap with your domain error
            raise

        except Exception:
            await self.session.rollback()
            raise


    async def get_asset_by_host_name(self, host_name: str) -> Asset | None:
        result = await self.session.execute(
            select(Asset).where(Asset.host_name == host_name)
        )
        return result.scalar_one_or_none()

    async def get_asset(self, asset_id: int) -> Asset | None:
        result = await self.session.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def list_assets(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        sort_by: str = "id", 
        order: str = "asc",
        search: str | None = None,
        asset_type: str | None = None
    ) -> list[Asset]:
        from sqlalchemy import asc, desc, or_
        
        query = select(Asset)
        
        # Filtering
        if asset_type and asset_type != "All":
            query = query.where(Asset.asset_type == asset_type)
            
        if search:
            search_filter = or_(
                Asset.host_name.ilike(f"%{search}%"),
                Asset.model.ilike(f"%{search}%"),
                Asset.make.ilike(f"%{search}%"),
                Asset.company_name.ilike(f"%{search}%"),
                Asset.serial_num.ilike(f"%{search}%"),
                Asset.location.ilike(f"%{search}%"),
                Asset.mac_id.ilike(f"%{search}%"),
                Asset.status.ilike(f"%{search}%"),
                Asset.u_uid.ilike(f"%{search}%"),
                func.cast(Asset.assetno, String).ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Handle sorting
        if hasattr(Asset, sort_by):
            col = getattr(Asset, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(col))
            else:
                query = query.order_by(asc(col))
        
        # Handle pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_active_assets(self) -> list[Asset]:
        result = await self.session.execute(
            select(Asset).where((Asset.is_allocated == True) & (Asset.is_deleted == False))
        )
        return result.scalars().all()

    async def delete_asset(self, asset_id: int) -> None:
        asset = await self.get_asset(asset_id)
        if asset:
            await self.session.delete(asset)
            await self.session.commit()

    async def update_asset(self, asset_id: int, modified_by: str | None = None, **kwargs) -> Asset | None:
        asset = await self.get_asset(asset_id)
        if asset:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(asset, key, value)
            asset.modified_by = modified_by
            asset.modified_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(asset)
        return asset
    async def count_incomplete_assets(self, user_name: str) -> int:
        from sqlalchemy import or_
        query = select(func.count()).select_from(Asset).where(
            or_(Asset.created_by == user_name, Asset.modified_by == user_name)
        ).where(
            or_(
                Asset.host_name.is_(None), Asset.host_name == "",
                Asset.make.is_(None), Asset.make == "",
                Asset.model.is_(None), Asset.model == "",
                Asset.location.is_(None), Asset.location == ""
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_incomplete_assets_uuids(self, user_name: str) -> list[str]:
        from sqlalchemy import or_
        query = select(Asset.u_uid).select_from(Asset).where(
            or_(Asset.created_by == user_name, Asset.modified_by == user_name)
        ).where(
            or_(
                Asset.host_name.is_(None), Asset.host_name == "",
                Asset.make.is_(None), Asset.make == "",
                Asset.model.is_(None), Asset.model == "",
                Asset.location.is_(None), Asset.location == ""
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_expired_warranty_assets(self) -> int:
        from datetime import date
        today = date.today()
        query = select(func.count()).select_from(Asset).where(
            (Asset.warranty_end_date.is_not(None)) & (Asset.warranty_end_date < today) & (Asset.is_deleted == False)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_expired_warranty_assets_hostnames(self) -> list[str]:
        from datetime import date
        today = date.today()
        query = select(Asset.host_name).select_from(Asset).where(
            (Asset.warranty_end_date.is_not(None)) & (Asset.warranty_end_date < today) & (Asset.is_deleted == False)
        )
        result = await self.session.execute(query)
        return [row for row in result.scalars().all() if row] # Filter out None/empty hostnames

    async def get_asset_summary_by_category(self) -> list[dict]:
        from sqlalchemy import case
        
        # Group by asset_type and count by status using CASE statements
        query = select(
            Asset.asset_type,
            func.sum(case((Asset.status.ilike('In-Stock'), 1), else_=0)).label('in_stock'),
            func.sum(case((Asset.status.ilike('Allocated'), 1), else_=0)).label('allocated'),
            func.sum(case((Asset.status.ilike('Retired'), 1), else_=0)).label('retired'),
            func.count().label('total')
        ).group_by(Asset.asset_type)
        
        result = await self.session.execute(query)
        summary = []
        for row in result.all():
            asset_type, in_stock, allocated, retired, total = row
            # Ensure None values from SUM(CASE) are treated as 0
            in_stock = int(in_stock or 0)
            allocated = int(allocated or 0)
            retired = int(retired or 0)
            
            # Calculation: ((Allocated + Retired) / (Allocated + Retired + In-stock)) * 100
            denominator = (allocated + retired + in_stock)
            consumption = 0
            if denominator > 0:
                consumption = ((allocated + retired) / denominator) * 100
            
            summary.append({
                "category": asset_type,
                "in_stock": in_stock,
                "allocated": allocated,
                "retired": retired,
                "total": total,
                "consumption": round(consumption, 2)
            })
        return summary
