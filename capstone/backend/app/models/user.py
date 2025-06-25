from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    LEGAL_ADMIN = "Legal Admin"
    LAWYER = "Lawyer"
    PARALEGAL = "Paralegal"
    CLIENT = "Client"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.CLIENT


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
