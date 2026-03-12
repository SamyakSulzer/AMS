# database/mappers/asset_map.py
from sqlalchemy import String, Integer, Boolean, DateTime, Date, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, date
from database.models.db import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    serial_num: Mapped[str] = mapped_column(String(100), nullable=False)
    host_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    make: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(String(30), nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    warranty_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    warranty_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_issued: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    u_uid: Mapped[str] = mapped_column(String(50), nullable=False)
    mac_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)
    modified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remarks: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_allocated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    staging_status: Mapped[str | None] = mapped_column(String(50), nullable=True, default='Not Staged')
    status: Mapped[str | None] = mapped_column(String(50), nullable=True, default='In-Stock')

    __table_args__ = (
        Index('idx_asset_type', 'asset_type'),
        Index('idx_model', 'model'),
        Index('idx_location_assets', 'location'),
        Index('idx_serial_number', 'serial_num'),
        Index('idx_assets_staging_status', 'staging_status'),
        Index('idx_assets_not_deleted', 'id', postgresql_where=(is_deleted == False)),
        Index('idx_assets_uuid', 'u_uid'),
        Index('idx_assets_mac_id', 'mac_id'),
        Index('idx_assets_active_inventory', 'status', 'staging_status', postgresql_where=(is_deleted == False)),
    )
