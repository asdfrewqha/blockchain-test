import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.sql import func

from backend.core.config import DEFAULT_AVATAR_URL
from backend.models.schemas import Role

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    avatar_url: Mapped[str] = mapped_column(String, nullable=False, default=DEFAULT_AVATAR_URL)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    encrypted_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    polls = relationship("Poll", backref="user", cascade="all, delete")
    votes = relationship("Vote", back_populates="user", cascade="all, delete")
    comments = relationship("Comment", back_populates="user", cascade="all, delete")


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_username: Mapped[str] = mapped_column(String, nullable=False)
    votes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    options: Mapped[list] = mapped_column(JSON, nullable=False)
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_notified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hashtags: Mapped[list] = mapped_column(JSONB, nullable=True)

    votes = relationship("Vote", back_populates="poll", cascade="all, delete")
    comment_list = relationship("Comment", back_populates="poll", cascade="all, delete")


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    poll_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("polls.id", ondelete="CASCADE"),
        index=True,
    )
    notification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_notified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    voted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=func.now()
    )

    user = relationship("User", back_populates="votes")
    poll = relationship("Poll", back_populates="votes")

    __table_args__ = (UniqueConstraint("user_id", "poll_id", name="uq_vote_user_poll"),)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    poll_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("polls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    user_username: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    parent_username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    replies_count: Mapped[int] = mapped_column(default=0, nullable=False)

    user = relationship("User", back_populates="comments")
    poll = relationship("Poll", back_populates="comment_list")
