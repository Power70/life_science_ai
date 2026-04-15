from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    response: str
    tool_used: str | None = None
    tool_result: dict | None = None
    tool_results: list[dict] | None = None
    form_updates: dict = Field(default_factory=dict)
