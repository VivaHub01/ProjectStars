from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.project.project_research.schemas import (
    ResearchQuestionResponse,
    ResearchAnswerCreate,
    ResearchAnswerResponse,
    ResearchProjectResponse,
    ResearchProgress
)
from src.project.project_research.service import (
    get_research_questions,
    get_research_project,
    create_research_project,
    save_research_answers,
    advance_research_stage,
    check_stage_completion
)


project_research_router = APIRouter(prefix="/research", tags=["research"])


@project_research_router.get("/questions/{phase}/{stage}", response_model=List[ResearchQuestionResponse])
async def get_questions_for_stage(
    phase: str,
    stage: str,
    db: AsyncSession = Depends(get_async_session)
):
    questions = await get_research_questions(db, phase, stage)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this stage")
    return questions


@project_research_router.get("/project/{project_id}", response_model=ResearchProjectResponse)
async def get_project_research(
    project_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    research_project = await get_research_project(db, project_id)
    if not research_project:
        research_project = await create_research_project(db, project_id)
    return research_project


@project_research_router.post("/answers/{research_project_id}", response_model=List[ResearchAnswerResponse])
async def save_answers(
    research_project_id: int,
    answers: List[ResearchAnswerCreate],
    db: AsyncSession = Depends(get_async_session)
):
    try:
        return await save_research_answers(db, research_project_id, answers)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@project_research_router.post("/progress/{research_project_id}", response_model=ResearchProjectResponse)
async def update_progress(
    research_project_id: int,
    next_phase: str,
    next_stage: str,
    db: AsyncSession = Depends(get_async_session)
):
    # First verify all questions are answered
    current_project = await get_research_project(db, research_project_id)
    if not current_project:
        raise HTTPException(status_code=404, detail="Research project not found")
    
    is_complete = await check_stage_completion(
        db,
        research_project_id,
        current_project.current_phase,
        current_project.current_stage
    )
    
    if not is_complete:
        raise HTTPException(
            status_code=400,
            detail="Cannot advance - not all questions answered for current stage"
        )
    
    return await advance_research_stage(db, research_project_id, next_phase, next_stage)


@project_research_router.get("/progress/{research_project_id}", response_model=ResearchProgress)
async def check_progress(
    research_project_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    project = await get_research_project(db, research_project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")
    
    is_complete = await check_stage_completion(
        db,
        research_project_id,
        project.current_phase,
        project.current_stage
    )
    
    return ResearchProgress(
        phase=project.current_phase,
        stage=project.current_stage,
        completed=is_complete
    )