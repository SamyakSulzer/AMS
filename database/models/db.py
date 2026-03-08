# database/models/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from urllib.parse import quote_plus

password = quote_plus("Password@9001")
#DATABASE_URL =  "postgresql://postgres:{password}@localhost:5432/AMS_try"  (old)
DATABASE_URL =  f"postgresql+asyncpg://postgres:{password}@localhost:5432/AMS_try"

# Base class for ORM models
class Base(DeclarativeBase):
    pass

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)

# server = AMS
# database = AMS_try
#password = Password@9001