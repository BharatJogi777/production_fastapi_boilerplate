from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True,
    pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)
SessionFactory = async_sessionmaker(engine, class_=AsyncSession,
    expire_on_commit=False, autoflush=False)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session
