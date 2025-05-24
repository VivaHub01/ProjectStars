from fastapi import APIRouter, Depends, HTTPException, status
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
from src.auth.models import User
from src.auth.service import AuthService

project_router = APIRouter(prefix="/projects", tags=["projects"])

@project_router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    try:
        return await create_project(db, project, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@project_router.get("/", response_model=List[ProjectResponse])
async def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    return await get_projects(db, current_user.id, skip, limit)

@project_router.get("/{project_id}", response_model=ProjectResponse)
async def read_single_project(
    project_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    return project

@project_router.put("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: int,
    project: ProjectCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    try:
        db_project = await update_project(db, project_id, project, current_user.id)
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return db_project
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@project_router.delete("/{project_id}")
async def remove_project(
    project_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    try:
        success = await delete_project(db, project_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return {"message": "Project deleted successfully"}
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )