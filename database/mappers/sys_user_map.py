from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from database.models.db import Base

class SysUser(Base):
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    pass_: Mapped[str] = mapped_column("pass", String(50), nullable=False)
    user_emp_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_emp_name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_role: Mapped[str] = mapped_column(String(50), nullable=False)
