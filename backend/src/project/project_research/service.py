from typing import List, Optional, Tuple
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.project.project_research.models import ResearchProject, ResearchQuestion, ResearchAnswer
from src.project.project_research.schemas import ResearchAnswerCreate, QuestionType

async def get_research_questions(
    db: AsyncSession,
    phase: str,
    stage: str
) -> List[ResearchQuestion]:
    result = await db.execute(
        select(ResearchQuestion)
        .where(
            ResearchQuestion.phase == phase,
            ResearchQuestion.stage == stage
        )
        .order_by(ResearchQuestion.order)
    )
    return result.scalars().all()

async def get_research_project_with_answers(
    db: AsyncSession,
    project_id: int
) -> Optional[ResearchProject]:
    result = await db.execute(
        select(ResearchProject)
        .options(selectinload(ResearchProject.answers))
        .where(ResearchProject.project_id == project_id)
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
    # Delete existing answers for these questions
    question_ids = [a.question_id for a in answers]
    await db.execute(
        delete(ResearchAnswer)
        .where(
            ResearchAnswer.research_project_id == research_project_id,
            ResearchAnswer.question_id.in_(question_ids)
        )
    )
    
    # Add new answers
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
    
    # Refresh all answers
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
    if not db_research_project:
        raise ValueError("Research project not found")
    
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
) -> Tuple[bool, int, int, bool]:
    # Get all required questions for this stage
    questions = await get_research_questions(db, phase, stage)
    required_questions = [q for q in questions if q.required]
    question_ids = [q.id for q in required_questions]
    
    # Check answers for required questions
    result = await db.execute(
        select(ResearchAnswer)
        .where(
            ResearchAnswer.research_project_id == research_project_id,
            ResearchAnswer.question_id.in_(question_ids)
        )
    )
    answers = result.scalars().all()
    
    # Calculate completion status
    required_answered = len(answers) >= len(required_questions)
    total_answered = len(answers)
    total_questions = len(questions)
    
    # Check if all required questions are answered
    return (
        required_answered,
        total_answered,
        total_questions,
        required_answered and (total_answered == total_questions)
    )

async def initialize_research_questions(db: AsyncSession):
    """Initialize the database with research questions"""
    # First clear existing questions
    await db.execute(delete(ResearchQuestion))
    
    questions = [
        ResearchQuestion(
            phase="planning",
            stage="stage_1",
            question_text="What is the main research question?",
            question_type=QuestionType.TEXT.value,
            order=1,
            required=True
        ),
        # Add other questions similarly...
    ]
    
    db.add_all(questions)
    await db.commit()