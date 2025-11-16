from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..core.jwt_handler import verify_admin_role, verify_token
from ..core.rate_limiter import rate_limiter

security = HTTPBearer()


async def verify_auth_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """Verify JWT Token"""
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")
    return verify_token(credentials.credentials)


async def verify_admin_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """Verify JWT Token And确保是 admin Role"""
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")
    return verify_admin_role(credentials.credentials)


async def apply_rate_limit(request: Request):
    """应用限流"""
    await rate_limiter.check_rate_limit(request)


def get_token_from_request(request: Request) -> Optional[str]:
    """从请求中提取 Token"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None
