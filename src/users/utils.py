from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from ..admin.models import UserType
from ..admin.utils import logger, security, verify_token


def require_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Check if credentials are missing (no bearer token provided)
    if credentials is None:
        logger.warning("Authentication attempt without bearer token - returning 401")
        raise HTTPException(status_code=401, detail="Authentication required")

    logger.info(
        f"Authentication attempt with token for user type: {credentials.credentials[:20]}..."
    )
    payload = verify_token(credentials)
    user_type = payload.get("type")
    if user_type != UserType.user.value:
        logger.warning(
            f"Non-user attempted to access user endpoint - user_type: {user_type}"
        )
        raise HTTPException(status_code=401, detail="User access required")
    logger.info(f"User authentication successful for user type: {user_type}")
    return payload

