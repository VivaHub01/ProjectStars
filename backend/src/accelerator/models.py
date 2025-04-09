from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.db.database import Base


class Accelerator(Base):
    __tablename__ = "accelerators"

    id: Mapped[int] = mapped_column(primary_key=True)
    university: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    projects: Mapped[list["Project"]] = relationship(back_populates="accelerator")