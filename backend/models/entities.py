import uuid
from datetime import date, datetime, time

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    specialty: Mapped[str | None] = mapped_column(String(100), nullable=True)
    institution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    territory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="hcp", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hcp_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("hcps.id"), nullable=True)
    interaction_type: Mapped[str] = mapped_column(String(50), default="Meeting")
    interaction_date: Mapped[date] = mapped_column(Date, default=date.today)
    interaction_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    attendees: Mapped[list[str]] = mapped_column(JSON, default=list)
    topics_discussed: Mapped[str] = mapped_column(Text, default="")
    materials_shared: Mapped[list[dict]] = mapped_column(JSON, default=list)
    samples_distributed: Mapped[list[dict]] = mapped_column(JSON, default=list)
    sentiment: Mapped[str] = mapped_column(String(20), default="Neutral")
    outcomes: Mapped[str] = mapped_column(Text, default="")
    follow_up_actions: Mapped[list[dict]] = mapped_column(JSON, default=list)
    ai_suggested_followups: Mapped[list[dict]] = mapped_column(JSON, default=list)
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    logged_via: Mapped[str] = mapped_column(String(20), default="chat")
    raw_chat_input: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hcp: Mapped[HCP | None] = relationship(back_populates="interactions")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    tool_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tool_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
