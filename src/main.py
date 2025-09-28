from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from alembic.config import Config
from alembic import command

app = FastAPI(title="BeliMang!", version="1.0.0")

# TODO: Add feature routers here
from .admin.router import router as admin_router
# from .users.router import users_router
# from .files.router import files_router

app.include_router(admin_router, prefix="/admin", tags=["Authentication"])
# app.include_router(users_router, prefix="/users", tags=["Users"])
# app.include_router(files_router, prefix="/files", tags=["Files"])

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
        sync_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        alembic_cfg.set_main_option("sqlalchemy.url", sync_url)
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Migration failed: {e}")
        # Continue startup even if migration fails

@app.get("/")
def read_root():
    return {"message": "Welcome to BeliMang!"}