from fastapi import Depends, HTTPException, status
from jose import JWTError

from app.core.security import decode_access_token
from app.database.deps import get_db


def get_current_user(token: str):

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return payload


def require_user(current_user=Depends(get_current_user)):
    return current_user


def require_admin(current_user=Depends(get_current_user)):

    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return current_user