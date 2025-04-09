from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.admin.schemas import AdminCreate, AdminResponse, AdminDeleteResponse
from src.auth.schemas import Token, Role
from src.accelerator.schemas import AcceleratorInDB, AcceleratorCreate, AcceleratorUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.admin.service import create_admin_account, delete_admin_account
from src.auth.service import authenticate_user, create_access_token, create_refresh_token
from src.accelerator.service import get_accelerator_by_university, update_accelerator_by_university, delete_accelerator_by_university
from src.db.database import get_async_session
from src.auth.service import allow_superadmin
from src.auth.models import User
from src.core.config import settings


admin_router = APIRouter(prefix="/admin", tags=["Admin Panel"])


@admin_router.post('/login', response_model=Token)
async def admin_login(
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
    
    if db_user.role not in [Role.admin, Role.superadmin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "email": db_user.email, 
            "role": db_user.role,
            "scopes": ["admin"]
        },
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


@admin_router.post("/", response_model=AdminResponse, dependencies=[Depends(allow_superadmin)])
async def create_admin(
    admin_data: AdminCreate,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_superadmin)
):
    return await create_admin_account(admin_data, db_session, current_user)


@admin_router.delete("/{email}", response_model=AdminDeleteResponse, dependencies=[Depends(allow_superadmin)])
async def delete_admin(
    email: str,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_superadmin)
):
    return await delete_admin_account(email, db_session, current_user)


@admin_router.post("/accelerators", response_model=AcceleratorInDB, dependencies=[Depends(allow_superadmin)])
async def create_accelerator(
    accelerator: AcceleratorCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_superadmin)
):
    existing_accelerator = await get_accelerator_by_university(db, accelerator.university)
    if existing_accelerator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accelerator for this university already exists"
        )
    return await create_accelerator(db, accelerator)


@admin_router.put("/accelerators/{university}", response_model=AcceleratorInDB, dependencies=[Depends(allow_superadmin)])
async def update_accelerator(
    university: str,
    accelerator: AcceleratorUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_superadmin)
):
    updated = await update_accelerator_by_university(db, university, accelerator)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accelerator not found"
        )
    return updated


@admin_router.delete("/accelerators/{university}", dependencies=[Depends(allow_superadmin)])
async def delete_accelerator(
    university: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_superadmin)
):
    success = await delete_accelerator_by_university(db, university)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accelerator not found"
        )
    return {"message": "Accelerator deleted successfully"}


@admin_router.post("/accelerators/{university}/toggle-status", response_model=AcceleratorInDB, dependencies=[Depends(allow_superadmin)])
async def toggle_accelerator_status(
    university: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_superadmin)
):
    result = await toggle_accelerator_status(db, university)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accelerator not found"
        )
    return result