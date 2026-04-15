from typing import Any
from typing_extensions import TypedDict


class AgentState(TypedDict):
    message: str
    session_id: str
    context: dict[str, Any]
    route: dict[str, Any]
    tool_result: dict[str, Any]
    response: str
