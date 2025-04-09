from pydantic import BaseModel, EmailStr
from enum import Enum


class Role(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"
    superadmin = "superadmin"


class UserOut(BaseModel):
    email: EmailStr
    role: Role
    disabled: bool


class UserInDB(UserOut):
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role


class UserResponse(BaseModel):
    email: EmailStr
    role: Role
    is_verified: bool
    disabled: bool
    

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserVerifiedResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str