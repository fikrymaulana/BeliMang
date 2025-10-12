import logging
import sys
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from alembic import command
from alembic.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from .admin.router import router as admin_router
from .files.router import router as files_router
from .merchants.items.router import router as item_router
from .merchants.router import (
    admin_router as admin_merchants_router,
)
from .merchants.router import (
    nearby_router as nearby_merchants_router,
)
from .users.router import (
    router_auth as users_auth_router,
)
from .users.router import (
    router_purchase as users_purchase_router,
)

app = FastAPI(title="BeliMang!", version="1.0.0")

logger.info("FastAPI application instance created successfully")


app.include_router(admin_router, prefix="/admin", tags=["Admin Authentication"])
app.include_router(users_auth_router, prefix="/users", tags=["User Authentication"])
app.include_router(users_purchase_router, prefix="/users", tags=["Purchase"])
app.include_router(files_router, prefix="", tags=["Image Upload"])
app.include_router(nearby_merchants_router, prefix="/merchants", tags=["Purchase"])
app.include_router(
    admin_merchants_router, prefix="/admin/merchants", tags=["Manage Merchants"]
)
app.include_router(
    item_router,
    prefix="/admin/merchants/{merchant_id}/items",
    tags=["Manage Merchants"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": "Bad Request"})


@app.on_event("startup")
async def run_migrations():
    import asyncio

    from .config import settings

    logger.info("Starting application startup process...")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Debug mode: {settings.debug}")

    try:
        logger.info("Running database migrations...")
        alembic_cfg = Config("alembic.ini")

        # Use the sync URL for alembic - PostgreSQL only
        database_url = settings.database_url
        if database_url.startswith("postgresql+asyncpg://"):
            # Convert async PostgreSQL URL back to sync for alembic
            sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif database_url.startswith("postgresql://"):
            # Already a sync PostgreSQL URL
            sync_url = database_url
        else:
            logger.error(f"Expected PostgreSQL URL for migrations, got: {database_url}")
            logger.error("Make sure DATABASE_URL is properly configured for PostgreSQL")
            # Use as-is and let alembic handle the error
            sync_url = database_url

        logger.info(f"Using sync database URL for migrations: {sync_url}")
        alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

        # Test database connection before running migrations
        logger.info("Testing database connection...")
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        # Continue startup even if migration fails


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed - application is responding to requests")
    return {"message": "Welcome to BeliMang!"}


@app.on_event("startup")
async def log_startup_complete():
    logger.info("=== APPLICATION STARTUP COMPLETE ===")
    logger.info("Server should now be listening on port 8000")
    logger.info("Ready to accept HTTP requests")
