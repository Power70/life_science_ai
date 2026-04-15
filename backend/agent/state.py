from typing import Any
from typing_extensions import TypedDict


class AgentState(TypedDict):
    message: str
    session_id: str
    context: dict[str, Any]
    db: Any
    route: dict[str, Any]
    tool_result: dict[str, Any]
    tool_results: list[dict[str, Any]]
    executed_tools: list[str]
    response: str
