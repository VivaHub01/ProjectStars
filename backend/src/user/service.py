from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.user.models import UserInfo
from src.user.schemas import UserInfoCreate, UserInfoUpdate


async def get_user_info_by_user_id(
    db: AsyncSession, 
    user_id: int
) -> UserInfo | None:
    result = await db.execute(select(UserInfo).filter(UserInfo.user_id == user_id))
    return result.scalars().first()


async def update_or_create_profile(
    db: AsyncSession,
    user_id: int,
    profile_data: UserInfoCreate | UserInfoUpdate
) -> UserInfo:
    existing_profile = await get_user_info_by_user_id(db, user_id)
    
    if existing_profile:
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_profile, field, value)
        db.add(existing_profile)
    else:
        existing_profile = UserInfo(
            user_id=user_id,
            **profile_data.model_dump(exclude_unset=True)
        )
        db.add(existing_profile)
    
    await db.commit()
    await db.refresh(existing_profile)
    return existing_profile