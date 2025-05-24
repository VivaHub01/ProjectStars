from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.auth.service import AuthService
from src.auth.models import User
from src.project.project_research.schemas import (
    ResearchQuestionResponse,
    ResearchAnswerCreate,
    ResearchAnswerResponse,
    ResearchProjectResponse,
    ResearchProgress,
    StageInfo
)
from src.project.project_research.service import (
    get_research_questions,
    get_research_project_with_answers,
    create_research_project,
    save_research_answers,
    advance_research_stage,
    check_stage_completion
)

project_research_router = APIRouter(
    prefix="/projects/{project_id}/research",
    tags=["research"]
)

@project_research_router.get("/questions/{phase}/{stage}", response_model=List[ResearchQuestionResponse])
async def get_questions_for_stage(
    project_id: int,
    phase: str,
    stage: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    questions = await get_research_questions(db, phase, stage)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions found for this stage"
        )
    return questions

@project_research_router.get("/", response_model=ResearchProjectResponse)
async def get_project_research(
    project_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    research_project = await get_research_project_with_answers(db, project_id)
    if not research_project:
        research_project = await create_research_project(db, project_id)
    return research_project

@project_research_router.post("/answers", response_model=List[ResearchAnswerResponse])
async def save_answers(
    project_id: int,
    answers: List[ResearchAnswerCreate],
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    research_project = await get_research_project_with_answers(db, project_id)
    if not research_project:
        research_project = await create_research_project(db, project_id)
    
    try:
        return await save_research_answers(
            db,
            research_project.id,
            answers
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@project_research_router.post("/progress", response_model=ResearchProjectResponse)
async def update_progress(
    project_id: int,
    next_phase: str,
    next_stage: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    research_project = await get_research_project_with_answers(db, project_id)
    if not research_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research project not found"
        )
    
    required_answered, answered, total, full_completion = await check_stage_completion(
        db,
        research_project.id,
        research_project.current_phase,
        research_project.current_stage
    )
    
    if not required_answered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot advance - required questions not answered"
        )
    
    try:
        return await advance_research_stage(
            db,
            research_project.id,
            next_phase,
            next_stage
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@project_research_router.get("/progress", response_model=ResearchProgress)
async def check_progress(
    project_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    research_project = await get_research_project_with_answers(db, project_id)
    if not research_project:
        research_project = await create_research_project(db, project_id)
    
    required_answered, answered, total, full_completion = await check_stage_completion(
        db,
        research_project.id,
        research_project.current_phase,
        research_project.current_stage
    )
    
    return ResearchProgress(
        phase=research_project.current_phase,
        stage=research_project.current_stage,
        completed=full_completion,
        answered_count=answered,
        total_questions=total,
        required_answered=required_answered
    )