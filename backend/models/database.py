from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        from backend.config import get_settings
        _engine = create_async_engine(
            get_settings().database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    return _engine


AsyncSessionLocal = async_sessionmaker(get_engine(), expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
