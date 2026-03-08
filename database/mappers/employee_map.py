from sqlalchemy import String, Integer, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from database.models.db import Base

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_no: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    cn1: Mapped[str] = mapped_column(String(150), nullable=True, unique=True)
    sam_name: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(254), nullable=True, unique=True)
    division: Mapped[str] = mapped_column(String(100), nullable=True)
    business_unit: Mapped[str] = mapped_column(String(100), nullable=True)
    cost_center: Mapped[str] = mapped_column(String(50), nullable=True)
    cost_center_description: Mapped[str] = mapped_column(String(50), nullable=True)
    physical_present: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    legal_entities: Mapped[str] = mapped_column(String(100), nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    joining_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_working_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    modified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

    # Core Identification Indexes
    __table_args__ = (
        Index('idx_emp_no', 'emp_no'),
        Index('idx_sam_name', 'sam_name'),
        Index('idx_email', 'email'),
        Index('idx_division', 'division'),
        Index('idx_business_unit', 'business_unit'),
        Index('idx_cost_center', 'cost_center'),
        Index('idx_location_emp', 'location'),
        Index('idx_active_employees', 'id', postgresql_where='is_active = TRUE'),
    )

