from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.auth.schemas import Role
from src.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(nullable=False)
    disabled: Mapped[bool] = mapped_column(default=True)
    reset_token: Mapped[str] = mapped_column(nullable=True)
    verification_token: Mapped[str] = mapped_column(nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)

    profile: Mapped["UserInfo"] = relationship("UserInfo", back_populates="user", uselist=False, cascade="all, delete-orphan")

    projects: Mapped[list["Project"]] = relationship(
        "Project", 
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )