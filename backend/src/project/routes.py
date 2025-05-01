from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.project.service import (
    create_project,
    get_project,
    get_projects,
    update_project,
    delete_project
)
from src.project.schemas import ProjectCreate, ProjectResponse
from src.db.database import get_async_session


project_router = APIRouter(prefix="/projects", tags=["projects"])


@project_router.post("/", response_model=ProjectResponse)
async def create_new_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        return await create_project(db, project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@project_router.get("/", response_model=List[ProjectResponse])
async def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session)
):
    return await get_projects(db, skip=skip, limit=limit)


@project_router.get("/{project_id}", response_model=ProjectResponse)
async def read_single_project(
    project_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    project = await get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@project_router.put("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: int,
    project: ProjectCreate,
    db: AsyncSession = Depends(get_async_session)
):
    db_project = await update_project(db, project_id, project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@project_router.delete("/{project_id}")
async def remove_project(
    project_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    if not await delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}