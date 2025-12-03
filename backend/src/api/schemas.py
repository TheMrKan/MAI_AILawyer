from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import uuid
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    sso_provider: str
    sso_id: str

    @validator('sso_provider')
    def validate_sso_provider(cls, v):
        allowed_providers = ["google"]
        if v not in allowed_providers:
            raise ValueError(f"Invalid SSO provider. Allowed: {allowed_providers}")
        return v

class UserResponse(UserBase):
    id: uuid.UUID
    sso_provider: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None


class ProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
