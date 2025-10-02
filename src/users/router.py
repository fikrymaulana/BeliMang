from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..purchases.schemas import EstimateResponse, EstimateRequest
from ..purchases.service import PurchaseService

from ..admin.models import UserType
from ..admin.utils import require_user_type
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


@router.post(
    "/estimate", response_model=EstimateResponse, status_code=status.HTTP_200_OK
)
async def post_users_estimate(
    body: EstimateRequest,
    session: AsyncSession = Depends(get_db),
):
    return await PurchaseService.calculate_estimate(session, body)
