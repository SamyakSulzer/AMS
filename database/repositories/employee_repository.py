# database/repositories/employee_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from database.mappers.employee_map import Employee
from sqlalchemy import select, func

class EmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_employees(self, search: str | None = None, is_active: bool | None = None) -> int:
        from sqlalchemy import or_
        query = select(func.count()).select_from(Employee)
        
        if is_active is not None:
            query = query.where(Employee.is_active == is_active)
            
        if search:
            search_filter = or_(
                Employee.cn1.ilike(f"%{search}%"),
                Employee.emp_no.ilike(f"%{search}%"),
                Employee.email.ilike(f"%{search}%"),
                Employee.business_unit.ilike(f"%{search}%"),
                Employee.division.ilike(f"%{search}%"),
                Employee.sam_name.ilike(f"%{search}%"),
                Employee.location.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            
        result = await self.session.execute(query)
        return result.scalar() or 0 

    async def add_employee(
        self,
        emp_no: str,
        cn1: str | None,
        email: str | None,
        sam_name: str | None,
        division: str | None,
        business_unit: str | None,
        cost_center: str | None,
        cost_center_description: str | None,
        legal_entities: str | None,
        location: str | None,
        joining_date: datetime | None,
        is_active: bool | None = True,
        created_by: str | None = None,
        modified_by: str | None = None,
        physical_present: bool = True,
        last_working_date: datetime | None = None,
    ) -> Employee:
        now = datetime.now(timezone.utc)
        employee = Employee(
            emp_no=emp_no,
            cn1=cn1,
            email=email,
            sam_name=sam_name,
            division=division,
            business_unit=business_unit,
            cost_center=cost_center,
            cost_center_description=cost_center_description,
            physical_present=physical_present,
            legal_entities=legal_entities,
            location=location,
            joining_date=joining_date,
            last_working_date=last_working_date,
            created_at=now,
            created_by=created_by,
            modified_at=now,
            is_active=is_active,
            modified_by=modified_by,
        )
        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        return employee

    async def get_employee_by_emp_no(self, emp_no: str) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.emp_no == emp_no)
        )
        return result.scalar_one_or_none()

    async def get_employee(self, employee_id: int) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    async def list_employees(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "id",
        order: str = "asc",
        search: str | None = None,
        is_active: bool | None = None
    ) -> list[Employee]:
        from sqlalchemy import asc, desc, or_

        query = select(Employee)

        # Filtering
        if is_active is not None:
            query = query.where(Employee.is_active == is_active)
            
        if search:
            search_filter = or_(
                Employee.cn1.ilike(f"%{search}%"),
                Employee.emp_no.ilike(f"%{search}%"),
                Employee.email.ilike(f"%{search}%"),
                Employee.business_unit.ilike(f"%{search}%"),
                Employee.division.ilike(f"%{search}%"),
                Employee.sam_name.ilike(f"%{search}%"),
                Employee.location.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        # Handle sorting
        if hasattr(Employee, sort_by):
            col = getattr(Employee, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(col))
            else:
                query = query.order_by(asc(col))

        # Handle pagination
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_employee(self, employee_id: int) -> None:
        employee = await self.get_employee(employee_id)
        if employee:
            await self.session.delete(employee)
            await self.session.commit()

    async def update_employee(self, employee_id: int, **kwargs) -> Employee | None:
        employee = await self.get_employee(employee_id)
        if employee:
            # Update modified_at automatically
            kwargs['modified_at'] = datetime.now(timezone.utc)
            for key, value in kwargs.items():
                if value is not None:
                    setattr(employee, key, value)
            await self.session.commit()
            await self.session.refresh(employee)
        return employee
