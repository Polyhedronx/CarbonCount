from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .carbon_zone import CarbonZoneBase


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "user"
    is_active: bool = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithZones(User):
    carbon_zones: list = []

    class Config:
        from_attributes = True


# 认证相关
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str