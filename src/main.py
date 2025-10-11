from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from alembic import command
from alembic.config import Config

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

    try:
        alembic_cfg = Config("alembic.ini")
        # Use the sync URL for alembic
        sync_url = settings.database_url.replace(
            "postgresql+asyncpg://", "postgresql://"
        )
        alembic_cfg.set_main_option("sqlalchemy.url", sync_url)
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Migration failed: {e}")
        # Continue startup even if migration fails


@app.get("/")
def read_root():
    return {"message": "Welcome to BeliMang!"}
