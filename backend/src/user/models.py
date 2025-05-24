from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from src.db.database import Base


class UserInfo(Base):
    __tablename__ = "user_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    surname: Mapped[str] = mapped_column(nullable=True)
    patronymic: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True, 
        index=True
    )
    user: Mapped["User"] = relationship("User", back_populates="profile")