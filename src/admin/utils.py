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

def require_user_type(required_type: UserType, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Check if credentials are missing (no bearer token provided)
    if credentials is None:
        logger.warning("Authentication attempt without bearer token - returning 401")
        raise HTTPException(status_code=401, detail="Authentication required")

    logger.info(f"Authentication attempt with token for user type: {credentials.credentials[:20]}...")
    payload = verify_token(credentials)
    user_type = payload.get("type")
    if user_type != required_type.value:
        logger.warning(f"User with type '{user_type}' attempted to access {required_type.value} endpoint")
        raise HTTPException(status_code=403, detail=f"{required_type.value.title()} access required")
    logger.info(f"Authentication successful for user type: {user_type} accessing {required_type.value} endpoint")
    return payload