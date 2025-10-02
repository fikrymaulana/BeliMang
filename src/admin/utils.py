import jwt
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..config import settings
from .models import UserType

security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Check if credentials are missing (no bearer token provided)
    if credentials is None:
        logger.warning("Authentication attempt without bearer token - returning 401")
        raise HTTPException(status_code=401, detail="Authentication required")

    logger.info(
        f"Authentication attempt with token for user type: {credentials.credentials[:20]}..."
    )
    payload = verify_token(credentials)
    user_type = payload.get("type")
    if user_type != UserType.admin.value:
        logger.warning(
            f"Non-admin user attempted to access admin endpoint - user_type: {user_type}"
        )
        raise HTTPException(status_code=401, detail="Admin access required")
    logger.info(f"Admin authentication successful for user type: {user_type}")
    return payload
