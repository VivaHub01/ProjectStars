from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.project.schemas import Type
from src.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[Type] = mapped_column(nullable=False)
    stage: Mapped[str] = mapped_column(nullable=False)
    
    accelerator_id: Mapped[int] = mapped_column(ForeignKey("accelerators.id"), nullable=True)
    accelerator: Mapped["Accelerator"] = relationship(back_populates="projects")