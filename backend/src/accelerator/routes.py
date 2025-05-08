from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.accelerator.schemas import AcceleratorInDB
from src.accelerator.service import get_accelerator_by_university, search_accelerators
from src.db.database import get_async_session
from src.auth.service import get_current_active_user, oauth2_user_scheme
from src.auth.models import User


accelerator_router = APIRouter(prefix="/accelerators", tags=["accelerators"])


@accelerator_router.get("/", response_model=List[AcceleratorInDB], dependencies=[Depends(oauth2_user_scheme)])
async def search_accelerators(
    search: Optional[str] = Query(None, description="Search by university name"),
    active_only: bool = Query(True, description="Show only active accelerators"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    return await search_accelerators(
        db,
        search_term=search,
        active_only=active_only,
        skip=skip,
        limit=limit
    )


@accelerator_router.get("/{university}", response_model=AcceleratorInDB, dependencies=[Depends(oauth2_user_scheme)])
async def get_accelerator(
    university: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    accelerator = await get_accelerator_by_university(db, university)
    if not accelerator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accelerator not found"
        )
    return accelerator