from pydantic import BaseModel, EmailStr
from src.auth.schemas import Role

class AdminCreate(BaseModel):
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    email: EmailStr
    role: Role
    is_verified: bool
    disabled: bool

class AdminDeleteResponse(BaseModel):
    message: str