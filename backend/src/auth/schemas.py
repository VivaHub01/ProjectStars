from pydantic import BaseModel, EmailStr, field_validator
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"
    superadmin = "superadmin"

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr

class UserBase(BaseModel):
    email: EmailStr
    role: Role

    @field_validator('email')
    def validate_email(cls, v):
        try:
            email_info = validate_email(v, check_deliverability=False)
            return email_info.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {str(e)}")

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserResponse(BaseModel):
    email: EmailStr
    role: Role
    disabled: bool

class UserInDB(UserBase):
    hashed_password: str
    created_at: datetime
    disabled: bool

class ResetPassword(BaseModel):
    token: str
    new_password: str
