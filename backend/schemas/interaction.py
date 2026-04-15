from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InteractionBase(BaseModel):
    hcp_id: UUID | None = None
    interaction_type: str = "Meeting"
    interaction_date: date
    interaction_time: time | None = None
    attendees: list[str] = Field(default_factory=list)
    topics_discussed: str = ""
    materials_shared: list[dict] = Field(default_factory=list)
    samples_distributed: list[dict] = Field(default_factory=list)
    sentiment: str = "Neutral"
    outcomes: str = ""
    follow_up_actions: list[dict] = Field(default_factory=list)
    ai_suggested_followups: list[dict] = Field(default_factory=list)
    ai_summary: str = ""
    logged_via: str = "chat"
    raw_chat_input: str = ""


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    interaction_type: str | None = None
    interaction_date: date | None = None
    interaction_time: time | None = None
    attendees: list[str] | None = None
    topics_discussed: str | None = None
    materials_shared: list[dict] | None = None
    samples_distributed: list[dict] | None = None
    sentiment: str | None = None
    outcomes: str | None = None
    follow_up_actions: list[dict] | None = None
    ai_suggested_followups: list[dict] | None = None
    ai_summary: str | None = None
    raw_chat_input: str | None = None


class InteractionResponse(InteractionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
