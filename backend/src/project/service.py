from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.project.models import Project
from src.project.schemas import ProjectCreate


async def create_project(db: AsyncSession, project: ProjectCreate) -> Project:
    db_project = Project(
        name=project.name,
        description=project.description,
        type=project.type,
        stage=project.stage
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
    result = await db.execute(select(Project).filter(Project.id == project_id))
    return result.scalars().first()


async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Project]:
    result = await db.execute(select(Project).offset(skip).limit(limit))
    return result.scalars().all()


async def update_project(
    db: AsyncSession, project_id: int, project: ProjectCreate
) -> Optional[Project]:
    db_project = await get_project(db, project_id)
    if db_project:
        db_project.name = project.name
        db_project.description = project.description
        db_project.type = project.type
        db_project.stage = project.stage
        await db.commit()
        await db.refresh(db_project)
    return db_project


async def delete_project(db: AsyncSession, project_id: int) -> bool:
    db_project = await get_project(db, project_id)
    if db_project:
        await db.delete(db_project)
        await db.commit()
        return True
    return False