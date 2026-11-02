from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    organization: str | None = None
    role: str = "developer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str | None = None
    organization: str | None = None
    role: str | None = None


__all__ = ["RegisterRequest", "LoginRequest", "TokenResponse"]
