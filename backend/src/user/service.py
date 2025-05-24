from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.user.models import UserInfo
from src.user.schemas import UserInfoCreate, UserInfoUpdate
from fastapi import HTTPException, status

async def get_user_info_by_user_id(
    db: AsyncSession, 
    user_id: int
) -> UserInfo | None:
    """Получить профиль пользователя по ID"""
    result = await db.execute(
        select(UserInfo)
        .where(UserInfo.user_id == user_id)
    )
    return result.scalars().first()

async def update_or_create_profile(
    db: AsyncSession,
    user_id: int,
    profile_data: UserInfoCreate | UserInfoUpdate,
    partial: bool = False
) -> UserInfo:
    """Обновить или создать профиль пользователя"""
    existing_profile = await get_user_info_by_user_id(db, user_id)
    
    if existing_profile:
        update_data = profile_data.model_dump(exclude_unset=partial)
        for field, value in update_data.items():
            setattr(existing_profile, field, value)
    else:
        if isinstance(profile_data, UserInfoUpdate) and not partial:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        existing_profile = UserInfo(
            user_id=user_id,
            **profile_data.model_dump(exclude_unset=True)
        )
    
    db.add(existing_profile)
    await db.commit()
    await db.refresh(existing_profile)
    return existing_profile

async def delete_user_profile(
    db: AsyncSession,
    user_id: int
) -> None:
    """Удалить профиль пользователя"""
    result = await db.execute(
        delete(UserInfo)
        .where(UserInfo.user_id == user_id)
    )
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    await db.commit()