from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config import settings


async_engine = create_async_engine(
    settings.DATABASE_URL_asyncpg,
    echo=True
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


async def get_async_session():
    async with async_session_factory() as session:
        yield session