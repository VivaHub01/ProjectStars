from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import timedelta
from src.db.database import get_async_session
from src.auth.schemas import Token, UserCreate, UserResponse, ResetPassword
from src.auth.service import (
    AuthService,
    EmailService,
    EmailTokenService,
    SecurityService,
)
from src.auth.models import User, VerificationToken, PasswordResetToken
from src.core.config import settings

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_async_session)):
    return await AuthService.create_user(db, user_data)

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    user = await AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not verified"
        )

    access_token_expires = timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = SecurityService.create_access_token(
        data={"email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = SecurityService.create_refresh_token(
        data={"email": user.email, "role": user.role},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_async_session)):
    try:
        payload = SecurityService.decode_refresh_token(refresh_token)
        user = await AuthService.get_user_by_email(db, payload['sub'])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        access_token_expires = timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = SecurityService.create_access_token(
            data={"email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@auth_router.post("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_async_session)):
    is_valid = await EmailTokenService.verify_token(db, token, 'verification')
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    result = await db.execute(
        select(VerificationToken)
        .where(VerificationToken.token == token)
    )
    verification_token = result.scalars().first()
    
    await db.execute(
        update(User)
        .where(User.id == verification_token.user_id)
        .values(disabled=False)
    )
    await EmailTokenService.mark_token_as_used(db, token, 'verification')
    await db.commit()
    
    return {"message": "Email verified successfully"}

@auth_router.post("/request-password-reset")
async def request_password_reset(email: str, db: AsyncSession = Depends(get_async_session)):
    user = await AuthService.get_user_by_email(db, email)
    if not user:
        return {"message": "If email exists, password reset link has been sent"}
    
    await EmailService.send_password_reset_email(db, email)
    return {"message": "If email exists, password reset link has been sent"}

@auth_router.post("/reset-password")
async def reset_password(data: ResetPassword, db: AsyncSession = Depends(get_async_session)):
    is_valid = await EmailTokenService.verify_token(db, data.token, 'password_reset')
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.token == data.token)
    )
    password_reset_token = result.scalars().first()
    
    hashed_password = SecurityService.get_password_hash(data.new_password)
    await db.execute(
        update(User)
        .where(User.id == password_reset_token.user_id)
        .values(hashed_password=hashed_password)
    )
    await EmailTokenService.mark_token_as_used(db, data.token, 'password_reset')
    await db.commit()