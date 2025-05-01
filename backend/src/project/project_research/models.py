from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.db.database import Base


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    current_phase: Mapped[str] = mapped_column(default="planning")
    current_stage: Mapped[str] = mapped_column(default="stage_1")
    
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="research_project")
    
    answers: Mapped[list["ResearchAnswer"]] = relationship(
        back_populates="research_project",
        cascade="all, delete-orphan"
    )


class ResearchQuestion(Base):
    __tablename__ = "research_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    phase: Mapped[str] = mapped_column(nullable=False)
    stage: Mapped[str] = mapped_column(nullable=False)
    question_text: Mapped[str] = mapped_column(nullable=False)
    question_type: Mapped[str] = mapped_column(nullable=False)  # text, multiple_choice, etc.
    options: Mapped[str] = mapped_column(nullable=True)  # JSON string for multiple choice options
    order: Mapped[int] = mapped_column(nullable=False)


class ResearchAnswer(Base):
    __tablename__ = "research_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer_text: Mapped[str] = mapped_column(nullable=False)
    
    question_id: Mapped[int] = mapped_column(ForeignKey("research_questions.id"))
    question: Mapped["ResearchQuestion"] = relationship()
    
    research_project_id: Mapped[int] = mapped_column(ForeignKey("research_projects.id"))
    research_project: Mapped["ResearchProject"] = relationship(back_populates="answers")