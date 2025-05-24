from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.db.database import Base


class Accelerator(Base):
    __tablename__ = "accelerators"

    id: Mapped[int] = mapped_column(primary_key=True)
    university: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    projects: Mapped[list["Project"]] = relationship(
        back_populates="accelerator", 
        cascade="all, delete-orphan"
    )