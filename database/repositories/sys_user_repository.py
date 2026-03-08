from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.mappers.sys_user_map import SysUser
from typing import Optional, List

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[SysUser]:
        query = select(SysUser).where(SysUser.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self, 
        username: str, 
        password: str, 
        user_emp_id: int, 
        user_emp_name: str, 
        user_role: str
    ) -> SysUser:
        user = SysUser(
            username=username,
            pass_=password,
            user_emp_id=user_emp_id,
            user_emp_name=user_emp_name,
            user_role=user_role
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_all_users(self) -> List[SysUser]:
        query = select(SysUser)
        result = await self.db.execute(query)
        return result.scalars().all()
