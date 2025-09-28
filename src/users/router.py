from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .schemas import UserRegister, UserLogin, TokenResponse
from .service import create_user, authenticate_user

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        result = await create_user(db, user_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        result = await authenticate_user(db, login_data.username, login_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))