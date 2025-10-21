from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..core.jwt_handler import verify_token, verify_admin_role
from ..core.rate_limiter import rate_limiter

security = HTTPBearer()

async def verify_auth_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """验证 JWT Token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
    return verify_token(credentials.credentials)

async def verify_admin_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """验证 JWT Token 并确保是 admin 角色"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
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