from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Registration请求"""

    username: str
    email: EmailStr
    password: str
    role_id: int


class RegisterResponse(BaseModel):
    """Registration响应"""

    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login请求"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token 响应"""

    access_token: str
    token_type: str = "bearer"
