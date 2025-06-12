from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from .config import config

engine = create_async_engine(config.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@asynccontextmanager
async def get_session():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
