from collections.abc import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Configure for PostgreSQL with asyncpg driver
database_url = settings.database_url
logger.info(f"Original database URL: {database_url}")

# Convert to async PostgreSQL URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info(f"Adjusted for async PostgreSQL: {database_url}")
else:
    logger.error(f"Expected PostgreSQL URL, got: {database_url}")
    logger.error("Make sure DATABASE_URL environment variable is set correctly in Kubernetes")

logger.info(f"Final database URL before engine creation: {database_url}")
if "sqlite" in database_url:
    logger.warning("Database URL contains 'sqlite' - this will cause async driver error!")

engine = create_async_engine(database_url, echo=settings.debug)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
