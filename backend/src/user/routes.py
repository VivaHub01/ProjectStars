from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.user.service import (
    get_user_info_by_user_id, 
    update_or_create_profile,
    delete_user_profile
)
from .schemas import UserInfoCreate, UserInfoResponse, UserInfoUpdate
from src.db.database import get_async_session
from src.auth.service import AuthService
from src.auth.models import User

user_router = APIRouter(prefix="/profile", tags=["User Profile"])

@user_router.get("/", response_model=UserInfoResponse)
async def get_profile(
    current_user: User = Depends(AuthService.get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить профиль текущего пользователя"""
    profile = await get_user_info_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@user_router.post("/", response_model=UserInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: UserInfoCreate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Создать профиль пользователя"""
    existing_profile = await get_user_info_by_user_id(db, current_user.id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )
    return await update_or_create_profile(db, current_user.id, profile_data)

@user_router.put("/", response_model=UserInfoResponse)
async def update_profile(
    profile_data: UserInfoUpdate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Полное обновление профиля"""
    return await update_or_create_profile(db, current_user.id, profile_data)

@user_router.patch("/", response_model=UserInfoResponse)
async def partial_update_profile(
    profile_data: UserInfoUpdate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Частичное обновление профиля"""
    return await update_or_create_profile(db, current_user.id, profile_data)

@user_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: User = Depends(AuthService.get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удалить профиль пользователя"""
    await delete_user_profile(db, current_user.id)