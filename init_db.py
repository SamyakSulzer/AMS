import asyncio
from database.models.db import engine, Base
# Import all mappers to ensure they are registered with Base.metadata
from database.mappers.employee_map import Employee
from database.mappers.assets_map import Asset

from database.mappers.allocation_map import Allocation
from database.mappers.master_map import MasterKey, MasterValue
from database.mappers.sys_user_map import SysUser

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
