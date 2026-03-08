# database/repositories/allocation_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc
from datetime import datetime, timezone
from database.mappers.allocation_map import Allocation
from database.mappers.employee_map import Employee
from database.mappers.assets_map import Asset

class AllocationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_asset_allocated(self, asset_id: int) -> bool:
        query = select(func.count()).select_from(Allocation).where(
            Allocation.asset_id == asset_id,
            Allocation.returned_at == None
        )
        result = await self.session.execute(query)
        count = result.scalar() or 0
        return count > 0

    async def count_allocations(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(Allocation).join(
            Employee, Allocation.employee_id == Employee.id
        ).join(
            Asset, Allocation.asset_id == Asset.id
        )
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Employee.cn1.ilike(search_filter)) |
                (Employee.emp_no.ilike(search_filter)) |
                (Asset.host_name.ilike(search_filter))
            )
            
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def add_allocation(
        self,
        employee_id: int,
        asset_id: int,
        allotted_at: datetime,
        returned_at: datetime | None = None,
        remarks: str | None = None,
        created_by: str | None = None,
        modified_by: str | None = None,
    ) -> Allocation:
        now = datetime.now(timezone.utc)
        allocation = Allocation(
            employee_id=employee_id,
            asset_id=asset_id,
            allotted_at=allotted_at,
            returned_at=returned_at,
            remarks=remarks,
            created_at=now,
            created_by=created_by,
            modified_at=now,
            modified_by=modified_by,
        )
        self.session.add(allocation)
        await self.session.commit()
        await self.session.refresh(allocation)
        return allocation

    async def get_allocation(self, allocation_id: int) -> Allocation | None:
        query = select(
            Allocation,
            Employee.emp_no,
            Employee.cn1.label("employee_name"),
            Asset.host_name,
            Asset.asset_type
        ).join(
            Employee, Allocation.employee_id == Employee.id
        ).join(
            Asset, Allocation.asset_id == Asset.id
        ).where(Allocation.id == allocation_id)
        
        result = await self.session.execute(query)
        row = result.first()
        if row:
            alloc, emp_no, emp_name, host_name, asset_type = row
            alloc.emp_no = emp_no
            alloc.employee_name = emp_name
            alloc.host_name = host_name
            alloc.asset_type = asset_type
            return alloc
        return None

    async def list_allocations(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "id",
        order: str = "asc",
        search: str | None = None
    ) -> list[Allocation]:
        query = select(
            Allocation,
            Employee.emp_no,
            Employee.cn1.label("employee_name"),
            Asset.host_name,
            Asset.asset_type
        ).join(
            Employee, Allocation.employee_id == Employee.id
        ).join(
            Asset, Allocation.asset_id == Asset.id
        )

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Employee.cn1.ilike(search_filter)) |
                (Employee.emp_no.ilike(search_filter)) |
                (Asset.host_name.ilike(search_filter))
            )

        # Handle sorting
        if hasattr(Allocation, sort_by):
            col = getattr(Allocation, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(col))
            else:
                query = query.order_by(asc(col))

        # Handle pagination
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        rows = result.all()
        
        allocations = []
        for alloc, emp_no, emp_name, host_name, asset_type in rows:
            alloc.emp_no = emp_no
            alloc.employee_name = emp_name
            alloc.host_name = host_name
            alloc.asset_type = asset_type
            allocations.append(alloc)
            
        return allocations

    async def delete_allocation(self, allocation_id: int) -> bool:
        allocation = await self.get_allocation(allocation_id)
        if allocation:
            await self.session.delete(allocation)
            await self.session.commit()
            return True
        return False

    async def update_allocation(self, allocation_id: int, **kwargs) -> Allocation | None:
        allocation = await self.get_allocation(allocation_id)
        if allocation:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(allocation, key, value)
            allocation.modified_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(allocation)
        return allocation
    async def get_asset_history(self, asset_id: int) -> list[Allocation]:
        query = select(
            Allocation,
            Employee.emp_no,
            Employee.cn1.label("employee_name"),
            Asset.host_name,
            Asset.asset_type
        ).join(
            Employee, Allocation.employee_id == Employee.id
        ).join(
            Asset, Allocation.asset_id == Asset.id
        ).where(Allocation.asset_id == asset_id).order_by(desc(Allocation.allotted_at))

        result = await self.session.execute(query)
        rows = result.all()
        
        history = []
        for alloc, emp_no, emp_name, host_name, asset_type in rows:
            alloc.emp_no = emp_no
            alloc.employee_name = emp_name
            alloc.host_name = host_name
            alloc.asset_type = asset_type
            history.append(alloc)
            
        return history
