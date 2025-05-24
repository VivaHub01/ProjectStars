from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON
from src.db.database import Base
from typing import List, Dict, Any

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    current_phase: Mapped[str] = mapped_column(default="planning")
    current_stage: Mapped[str] = mapped_column(default="stage_1")
    
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    project: Mapped["Project"] = relationship(back_populates="research_project")
    
    answers: Mapped[List["ResearchAnswer"]] = relationship(
        back_populates="research_project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class ResearchQuestion(Base):
    __tablename__ = "research_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    phase: Mapped[str] = mapped_column(nullable=False, index=True)
    stage: Mapped[str] = mapped_column(nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(nullable=False)
    question_type: Mapped[str] = mapped_column(nullable=False)
    options: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)
    required: Mapped[bool] = mapped_column(default=True)

    answers: Mapped[List["ResearchAnswer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan"
    )

class ResearchAnswer(Base):
    __tablename__ = "research_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer_text: Mapped[str] = mapped_column(nullable=False)
    
    question_id: Mapped[int] = mapped_column(
        ForeignKey("research_questions.id", ondelete="CASCADE")
    )
    question: Mapped["ResearchQuestion"] = relationship(back_populates="answers")
    
    research_project_id: Mapped[int] = mapped_column(
        ForeignKey("research_projects.id", ondelete="CASCADE")
    )
    research_project: Mapped["ResearchProject"] = relationship(back_populates="answers")