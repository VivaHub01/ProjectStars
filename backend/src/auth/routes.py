from datetime import timedelta
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.service import (
    get_user_by_email, 
    create_user, 
    authenticate_user, 
    create_access_token, 
    create_refresh_token, 
    verify_refresh_token,
    request_password_reset,
    reset_password,
    verify_email,
    oauth2_user_scheme,
)
from src.auth.schemas import UserCreate, UserResponse, Token, ResetPasswordRequest, ResetPasswordConfirm, UserVerifiedResponse, Role
from src.db.database import get_async_session
from src.core.config import settings


auth_router = APIRouter(tags=["Authentication"])


@auth_router.post('/register', response_model=UserResponse)
async def register(
    user: UserCreate,
    db_session: AsyncSession = Depends(get_async_session),
):
    if user.role not in [Role.student, Role.teacher]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only student and teacher registration is allowed"
        )
    existing_user = await get_user_by_email(db_session, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = await create_user(
        db_session=db_session,
        email=user.email,
        password=user.password,
        role=user.role
    )
    return new_user


@auth_router.get('/verify-email', response_model=UserVerifiedResponse)
async def verify_email_endpoint(
    token: str,
    db_session: AsyncSession = Depends(get_async_session),
):
    user = await verify_email(db_session, token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Email successfully verified"}


@auth_router.post('/login', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_async_session),
) -> Token:
    db_user = await authenticate_user(db_session, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if db_user.role in [Role.admin, Role.superadmin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    if not db_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification link.",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": db_user.email},
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"email": db_user.email},
        expires_delta=refresh_token_expires
    )
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@auth_router.post('/refresh', response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    db_session: AsyncSession = Depends(get_async_session),
) -> Token:
    user = await verify_refresh_token(refresh_token, db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": user.email}, 
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = create_refresh_token(
        data={"email": user.email}, 
        expires_delta=refresh_token_expires
    )
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@auth_router.post("/request-password-reset")
async def request_password_reset_endpoint(
    reset_request: ResetPasswordRequest,
    db_session: AsyncSession = Depends(get_async_session)
):
    user = await get_user_by_email(db_session, reset_request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await request_password_reset(db_session, user)
    return {"message": "Password reset link has been sent to your email."}


@auth_router.post("/reset-password")
async def reset_password_endpoint(
    reset_confirm: ResetPasswordConfirm,
    db_session: AsyncSession = Depends(get_async_session)
):
    user = await reset_password(db_session, reset_confirm.token, reset_confirm.new_password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password has been successfully reset."}