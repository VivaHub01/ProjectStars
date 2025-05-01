from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class QuestionType(str, Enum):
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"


class ResearchQuestionBase(BaseModel):
    phase: str
    stage: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    order: int


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


class ResearchProjectResponse(BaseModel):
    id: int
    current_phase: str
    current_stage: str
    project_id: int


class ResearchProgress(BaseModel):
    phase: str
    stage: str
    completed: bool