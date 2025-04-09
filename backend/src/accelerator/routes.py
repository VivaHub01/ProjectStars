from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.accelerator.schemas import AcceleratorInDB
from src.accelerator.service import get_accelerator_by_university, search_accelerators
from src.db.database import get_async_session


accelerator_router = APIRouter(prefix="/accelerators", tags=["accelerators"])


@accelerator_router.get("/", response_model=List[AcceleratorInDB])
async def search_accelerators(
    search: Optional[str] = Query(None, description="Search by university name"),
    active_only: bool = Query(True, description="Show only active accelerators"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session)
):
    return await search_accelerators(
        db,
        search_term=search,
        active_only=active_only,
        skip=skip,
        limit=limit
    )


@accelerator_router.get("/{university}", response_model=AcceleratorInDB)
async def get_accelerator(
    university: str,
    db: AsyncSession = Depends(get_async_session)
):
    accelerator = await get_accelerator_by_university(db, university)
    if not accelerator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accelerator not found"
        )
    return accelerator