from sqlalchemy.ext.asyncio import(
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from typing import Annotated, AsyncGenerator
from app.core.config import get_settings

settings = get_settings()

#Create asybc engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

#Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

#Dependency to get async session
async def get_db()->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise