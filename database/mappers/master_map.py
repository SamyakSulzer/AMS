from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.db import Base

class MasterKey(Base):
    __tablename__ = "master_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship to values (optional but good practice)
    values: Mapped[list["MasterValue"]] = relationship("MasterValue", back_populates="key", cascade="all, delete-orphan")


class MasterValue(Base):
    __tablename__ = "master_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key_id: Mapped[int] = mapped_column(ForeignKey("master_keys.id"), nullable=False, index=True)
    value: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Back reference to MasterKey
    key: Mapped["MasterKey"] = relationship("MasterKey", back_populates="values")
