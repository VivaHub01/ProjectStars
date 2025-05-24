from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from enum import Enum

class QuestionType(str, Enum):
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    SCALE = "scale"

class ResearchQuestionBase(BaseModel):
    phase: str = Field(..., example="planning")
    stage: str = Field(..., example="stage_1")
    question_text: str
    question_type: QuestionType
    options: Optional[Dict[str, List[str]]] = None
    order: int = Field(..., gt=0)
    required: bool = True

    @validator('options')
    def validate_options(cls, v, values):
        if values.get('question_type') in ['multiple_choice', 'checkbox'] and not v:
            raise ValueError("Options are required for multiple choice questions")
        return v

class ResearchQuestionCreate(ResearchQuestionBase):
    pass

class ResearchQuestionResponse(ResearchQuestionBase):
    id: int

class ResearchAnswerBase(BaseModel):
    answer_text: str
    question_id: int

class ResearchAnswerCreate(ResearchAnswerBase):
    pass

class ResearchAnswerResponse(ResearchAnswerBase):
    id: int
    research_project_id: int

class ResearchProjectResponse(BaseModel):
    id: int
    current_phase: str
    current_stage: str
    project_id: int
    answers: List[ResearchAnswerResponse] = []

class ResearchProgress(BaseModel):
    phase: str
    stage: str
    completed: bool
    answered_count: int
    total_questions: int
    required_answered: bool

class StageInfo(BaseModel):
    phase: str
    stage: str
    name: str
    description: str