from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import delete
from fastapi import HTTPException, status, Depends
from src.db.database import get_async_session
from src.auth.models import User
from src.auth.service import get_user_by_email, create_user, get_current_user, allow_superadmin
from src.auth.schemas import Role
from src.auth.admin.schemas import AdminCreate, AdminResponse, AdminDeleteResponse


oauth2_admin_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/admin/login",
    scheme_name="AdminAuth",
    scopes={"admin": "Admin access"},
)


async def create_admin_account(
    admin_data: AdminCreate,
    db_session: AsyncSession,
    current_user: User = Depends(allow_superadmin)
) -> AdminResponse:
    existing_user = await get_user_by_email(db_session, admin_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_admin = await create_user(
        db_session=db_session,
        email=admin_data.email,
        password=admin_data.password,
        role=Role.admin
    )
    
    new_admin.is_verified = True
    new_admin.disabled = False
    await db_session.commit()
    await db_session.refresh(new_admin)
    
    return AdminResponse(
        email=new_admin.email,
        role=new_admin.role,
        is_verified=new_admin.is_verified,
        disabled=new_admin.disabled
    )

async def delete_admin_account(
    email: str,
    db_session: AsyncSession,
    current_user: User = Depends(allow_superadmin)
) -> AdminDeleteResponse:
    if current_user.email == email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    admin_to_delete = await get_user_by_email(db_session, email)
    if not admin_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if admin_to_delete.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )
    
    await db_session.execute(delete(User).where(User.email == email))
    await db_session.commit()
    
    return AdminDeleteResponse(message="Admin account deleted successfully")


async def get_current_admin(
    token: Annotated[str, Depends(oauth2_admin_scheme)],
    db_session: AsyncSession = Depends(get_async_session),
) -> User:
    user = await get_current_user(token, db_session)
    if user.role not in [Role.admin, Role.superadmin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user

