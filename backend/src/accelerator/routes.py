from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.accelerator.schemas import (
    AcceleratorInDB,
    AcceleratorCreate,
    AcceleratorUpdate
)
from src.accelerator.service import (
    create_accelerator,
    get_accelerator_by_university,
    search_accelerators,
    update_accelerator_by_university,
    delete_accelerator_by_university,
    toggle_accelerator_status
)
from src.db.database import get_async_session
from src.auth.service import AuthService, allow_admin
from src.auth.models import User

accelerator_router = APIRouter(prefix="/accelerators", tags=["Accelerators"])

@accelerator_router.get("/", response_model=List[AcceleratorInDB])
async def search_accelerators_endpoint(
    search: str | None = Query(None),
    active_only: bool = Query(True),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    return await search_accelerators(
        db,
        search_term=search,
        active_only=active_only,
        skip=skip,
        limit=limit
    )

@accelerator_router.get("/{university}", response_model=AcceleratorInDB)
async def get_accelerator_endpoint(
    university: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    accelerator = await get_accelerator_by_university(db, university)
    if not accelerator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accelerator not found"
        )
    return accelerator

@accelerator_router.post("/", response_model=AcceleratorInDB, status_code=201)
async def create_accelerator_endpoint(
    accelerator: AcceleratorCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_admin)
):
    return await create_accelerator(db, accelerator)

@accelerator_router.put("/{university}", response_model=AcceleratorInDB)
async def update_accelerator_endpoint(
    university: str,
    accelerator: AcceleratorUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_admin)
):
    updated = await update_accelerator_by_university(db, university, accelerator)
    if not updated:
        raise HTTPException(status_code=404, detail="Accelerator not found")
    return updated

@accelerator_router.delete("/{university}", status_code=204)
async def delete_accelerator_endpoint(
    university: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_admin)
):
    if not await delete_accelerator_by_university(db, university):
        raise HTTPException(status_code=404, detail="Accelerator not found")

@accelerator_router.post("/{university}/toggle-status", response_model=AcceleratorInDB)
async def toggle_accelerator_status_endpoint(
    university: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(allow_admin)
):
    result = await toggle_accelerator_status(db, university)
    if not result:
        raise HTTPException(status_code=404, detail="Accelerator not found")
    return result