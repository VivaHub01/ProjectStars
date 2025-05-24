from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.accelerator.models import Accelerator
from src.accelerator.schemas import AcceleratorCreate, AcceleratorUpdate
from typing import List, Optional
from fastapi import HTTPException, status

async def create_accelerator(
    db: AsyncSession, 
    accelerator: AcceleratorCreate
) -> Accelerator:
    existing = await get_accelerator_by_university(db, accelerator.university)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accelerator with this university already exists"
        )
    
    db_accelerator = Accelerator(**accelerator.model_dump())
    db.add(db_accelerator)
    await db.commit()
    await db.refresh(db_accelerator)
    return db_accelerator

async def get_accelerator_by_university(
    db: AsyncSession, 
    university: str
) -> Optional[Accelerator]:
    result = await db.execute(
        select(Accelerator)
        .where(Accelerator.university.ilike(university))
    )
    return result.scalars().first()

async def search_accelerators(
    db: AsyncSession,
    search_term: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> List[Accelerator]:
    query = select(Accelerator)
    
    if active_only:
        query = query.where(Accelerator.is_active == True)
    
    if search_term:
        query = query.where(
            Accelerator.university.ilike(f"%{search_term}%")
        )
    
    result = await db.execute(
        query.order_by(Accelerator.university)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_accelerator_by_university(
    db: AsyncSession,
    university: str,
    accelerator: AcceleratorUpdate
) -> Optional[Accelerator]:
    db_accelerator = await get_accelerator_by_university(db, university)
    if not db_accelerator:
        return None
    
    update_data = accelerator.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_accelerator, key, value)
    
    await db.commit()
    await db.refresh(db_accelerator)
    return db_accelerator

async def delete_accelerator_by_university(
    db: AsyncSession, 
    university: str
) -> bool:
    result = await db.execute(
        delete(Accelerator)
        .where(Accelerator.university.ilike(university))
    )
    await db.commit()
    return result.rowcount > 0

async def toggle_accelerator_status(
    db: AsyncSession,
    university: str
) -> Optional[Accelerator]:
    db_accelerator = await get_accelerator_by_university(db, university)
    if not db_accelerator:
        return None
    
    db_accelerator.is_active = not db_accelerator.is_active
    await db.commit()
    await db.refresh(db_accelerator)
    return db_accelerator