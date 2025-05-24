from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.project.models import Project
from src.project.schemas import ProjectCreate, STAGE_MAPPING

async def create_project(db: AsyncSession, project: ProjectCreate, user_id: int,accelerator_id: Optional[int] = None) -> Project:
    db_project = Project(
        name=project.name,
        description=project.description,
        type=project.type,
        stage=project.stage or STAGE_MAPPING[project.type][0],
        user_id=user_id,
        accelerator_id=accelerator_id
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
    result = await db.execute(select(Project).filter(Project.id == project_id))
    return result.scalars().first()

async def get_projects(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
    result = await db.execute(
        select(Project)
        .where(Project.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_project(db: AsyncSession, project_id: int, project: ProjectCreate,user_id: int) -> Optional[Project]:
    db_project = await get_project(db, project_id)
    if not db_project:
        return None
    if db_project.user_id != user_id:
        raise PermissionError("Not authorized to update this project")
    
    for field, value in project.model_dump().items():
        setattr(db_project, field, value)
    
    await db.commit()
    await db.refresh(db_project)
    return db_project

async def delete_project(db: AsyncSession, project_id: int, user_id: int) -> bool:
    db_project = await get_project(db, project_id)
    if not db_project:
        return False
    if db_project.user_id != user_id:
        raise PermissionError("Not authorized to delete this project")
    
    await db.delete(db_project)
    await db.commit()
    return True