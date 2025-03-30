from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    email: EmailStr
    role: str
    disabled: bool


class UserInDB(UserOut):
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str


class UserResponse(BaseModel):
    email: EmailStr
    role: str
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