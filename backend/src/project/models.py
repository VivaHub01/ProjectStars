from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.project.schemas import ProjectType
from src.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[ProjectType] = mapped_column(nullable=False)
    stage: Mapped[str] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="projects")
    
    accelerator_id: Mapped[int] = mapped_column(
        ForeignKey("accelerators.id"), 
        nullable=True
    )
    accelerator: Mapped["Accelerator"] = relationship(back_populates="projects")

    research_project: Mapped["ResearchProject"] = relationship(
        "ResearchProject",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Project(id={self.id}, name={self.name}, type={self.type})"