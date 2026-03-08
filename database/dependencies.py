from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.db import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session.
    Yields:
        AsyncSession: SQLAlchemy async session.
    """
    async with AsyncSessionLocal() as session:
        yield session
