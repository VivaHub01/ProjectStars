from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from .service import get_user_info_by_user_id, update_or_create_profile
from .schemas import UserInfoCreate, UserInfoResponse, UserInfoUpdate
from src.db.database import get_async_session
from src.auth.service import get_current_active_user, oauth2_scheme
from src.auth.models import User


user_router = APIRouter(prefix="/profile", tags=["User Profile"])


@user_router.get( "", response_model=UserInfoResponse, dependencies=[Depends(oauth2_scheme)])
async def get_profile(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    profile = await get_user_info_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


@user_router.post( "", response_model=UserInfoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(oauth2_scheme)])
async def create_profile(
    profile_data: UserInfoCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    existing_profile = await get_user_info_by_user_id(db, current_user.id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists, use PUT or PATCH to update"
        )
    return await update_or_create_profile(db, current_user.id, profile_data)


@user_router.put( "", response_model=UserInfoResponse, dependencies=[Depends(oauth2_scheme)])
async def update_profile(
    profile_data: UserInfoUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    return await update_or_create_profile(db, current_user.id, profile_data)


@user_router.patch("", response_model=UserInfoResponse, dependencies=[Depends(oauth2_scheme)]) 
async def partial_update_profile(
    profile_data: UserInfoUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    return await update_or_create_profile(db, current_user.id, profile_data)