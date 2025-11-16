from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt

from .config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create访问 Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """VerifyAnd解析 Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing user_id")
        return payload
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")


def verify_admin_role(token: str) -> dict:
    """Verify Token And确保User是 admin Role"""
    payload = verify_token(token)
    role_id = payload.get("role")

    if role_id != 3:  # 3 是 admin Role ID
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Admin role required")

    return payload
