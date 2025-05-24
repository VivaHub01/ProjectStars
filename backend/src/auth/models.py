from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import datetime, timezone
from src.auth.schemas import Role
from src.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    disabled: Mapped[bool] = mapped_column(default=True)
    role: Mapped[Role] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    verification_token: Mapped["VerificationToken"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    password_reset_token: Mapped["PasswordResetToken"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    profile: Mapped["UserInfo"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    projects: Mapped["Project"] = relationship(back_populates="user", cascade="all, delete-orphan")


class VerificationToken(Base):
    __tablename__ = "verification_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="verification_token")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="password_reset_token")