from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import ResearchProject, ResearchQuestion, ResearchAnswer
from .schemas import (
    ResearchQuestionCreate,
    ResearchAnswerCreate,
    ResearchProjectResponse
)


async def get_research_questions(
    db: AsyncSession,
    phase: str,
    stage: str
) -> List[ResearchQuestion]:
    result = await db.execute(
        select(ResearchQuestion)
        .filter(ResearchQuestion.phase == phase, ResearchQuestion.stage == stage)
        .order_by(ResearchQuestion.order)
    )
    return result.scalars().all()


async def get_research_project(
    db: AsyncSession,
    project_id: int
) -> Optional[ResearchProject]:
    result = await db.execute(
        select(ResearchProject)
        .filter(ResearchProject.project_id == project_id)
    )
    return result.scalars().first()


async def create_research_project(
    db: AsyncSession,
    project_id: int
) -> ResearchProject:
    db_research_project = ResearchProject(project_id=project_id)
    db.add(db_research_project)
    await db.commit()
    await db.refresh(db_research_project)
    return db_research_project


async def save_research_answers(
    db: AsyncSession,
    research_project_id: int,
    answers: List[ResearchAnswerCreate]
) -> List[ResearchAnswer]:
    db_answers = [
        ResearchAnswer(
            research_project_id=research_project_id,
            question_id=answer.question_id,
            answer_text=answer.answer_text
        )
        for answer in answers
    ]
    
    db.add_all(db_answers)
    await db.commit()
    
    for answer in db_answers:
        await db.refresh(answer)
    
    return db_answers


async def advance_research_stage(
    db: AsyncSession,
    research_project_id: int,
    next_phase: str,
    next_stage: str
) -> ResearchProject:
    db_research_project = await db.get(ResearchProject, research_project_id)
    if db_research_project:
        db_research_project.current_phase = next_phase
        db_research_project.current_stage = next_stage
        await db.commit()
        await db.refresh(db_research_project)
    return db_research_project


async def check_stage_completion(
    db: AsyncSession,
    research_project_id: int,
    phase: str,
    stage: str
) -> bool:
    # Get all questions for this stage
    questions = await get_research_questions(db, phase, stage)
    question_ids = [q.id for q in questions]
    
    # Check if all questions have answers
    result = await db.execute(
        select(ResearchAnswer)
        .filter(
            ResearchAnswer.research_project_id == research_project_id,
            ResearchAnswer.question_id.in_(question_ids)
        )
    )
    answers = result.scalars().all()
    
    return len(answers) >= len(questions)


async def initialize_research_questions(db: AsyncSession):
    """Initialize the database with sample research questions"""
    questions = [
        # Planning Phase - Stage 1
        ResearchQuestion(
            phase="planning",
            stage="stage_1",
            question_text="What is the main research question?",
            question_type="text",
            order=1
        ),
        ResearchQuestion(
            phase="planning",
            stage="stage_1",
            question_text="What are your research objectives?",
            question_type="text",
            order=2
        ),
        
        # Planning Phase - Stage 2
        ResearchQuestion(
            phase="planning",
            stage="stage_2",
            question_text="What methodology will you use?",
            question_type="multiple_choice",
            options=["Qualitative", "Quantitative", "Mixed Methods"],
            order=1
        ),
        ResearchQuestion(
            phase="planning",
            stage="stage_2",
            question_text="Describe your data collection methods",
            question_type="text",
            order=2
        ),
        
        # Research Phase - Stage 1
        ResearchQuestion(
            phase="research",
            stage="stage_1",
            question_text="What data have you collected so far?",
            question_type="text",
            order=1
        ),
        ResearchQuestion(
            phase="research",
            stage="stage_1",
            question_text="Have you encountered any challenges?",
            question_type="text",
            order=2
        ),
        
        # Research Phase - Stage 2
        ResearchQuestion(
            phase="research",
            stage="stage_2",
            question_text="How are you analyzing the data?",
            question_type="text",
            order=1
        ),
        ResearchQuestion(
            phase="research",
            stage="stage_2",
            question_text="What preliminary findings do you have?",
            question_type="text",
            order=2
        ),
        
        # Implementation Phase - Stage 1
        ResearchQuestion(
            phase="implementation",
            stage="stage_1",
            question_text="How will you implement your findings?",
            question_type="text",
            order=1
        ),
        ResearchQuestion(
            phase="implementation",
            stage="stage_1",
            question_text="What are the practical applications?",
            question_type="text",
            order=2
        ),
        
        # Implementation Phase - Stage 2
        ResearchQuestion(
            phase="implementation",
            stage="stage_2",
            question_text="What are your conclusions?",
            question_type="text",
            order=1
        ),
        ResearchQuestion(
            phase="implementation",
            stage="stage_2",
            question_text="What future research directions do you recommend?",
            question_type="text",
            order=2
        ),
    ]
    
    db.add_all(questions)
    await db.commit()