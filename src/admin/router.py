from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .schemas import AdminRegister, AdminLogin, TokenResponse
from .service import create_admin, authenticate_admin

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(admin_data: AdminRegister, db: AsyncSession = Depends(get_db)):
    try:
        result = await create_admin(db, admin_data)
        return result
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

@router.post("/login", response_model=TokenResponse)
async def login_admin(login_data: AdminLogin, db: AsyncSession = Depends(get_db)):
    try:
        result = await authenticate_admin(db, login_data.username, login_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))