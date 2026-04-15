from langgraph.graph import END, START, StateGraph

from agent.state import AgentState
from agent.tools import TOOL_REGISTRY
from services.groq_client import groq_service

ROUTER_SCHEMA = '{"tools":["one of available tools"],"confidence":"0-1","reason":"string"}'
TOOLS_LIST = ", ".join(TOOL_REGISTRY.keys())
PRIMARY_FALLBACK = "log_interaction"


def _normalize_plan(route: dict, message: str) -> list[str]:
    planned_tools = route.get("tools") if isinstance(route, dict) else []
    if isinstance(planned_tools, str):
        planned_tools = [planned_tools]
    if not isinstance(planned_tools, list):
        planned_tools = []

    valid_tools = []
    for tool_name in planned_tools:
        if tool_name in TOOL_REGISTRY and tool_name not in valid_tools:
            valid_tools.append(tool_name)

    message_lower = message.lower()
    if any(token in message_lower for token in ["correct", "actually", "not today", "yesterday", "change", "update the date"]):
        if "edit_interaction" not in valid_tools:
            valid_tools.insert(0, "edit_interaction")
    if any(token in message_lower for token in ["search", "find", "look up", "other times", "last month", "history"]):
        if "search_interactions" not in valid_tools:
            valid_tools.append("search_interactions")
    if any(token in message_lower for token in ["summary", "summarize", "call summary"]):
        if "generate_call_summary" not in valid_tools:
            valid_tools.append("generate_call_summary")
    if any(token in message_lower for token in ["follow-up", "follow up", "next step", "next steps", "schedule", "revisit", "lunch", "meeting"]):
        if "schedule_followup_meeting" not in valid_tools and "suggest_follow_up" not in valid_tools:
            valid_tools.append("schedule_followup_meeting")

    if not valid_tools:
        valid_tools = [PRIMARY_FALLBACK]

    return valid_tools[:3]


async def router_node(state: AgentState) -> AgentState:
    prompt = (
        f"Pick the best tool or tools for this message. Tools: {TOOLS_LIST}. "
        "Return an ordered list of up to 3 tools. "
        "Use edit_interaction for corrections to existing form data. "
        "Use search_interactions for search/history requests. "
        "Use generate_call_summary for summary requests. "
        "Use schedule_followup_meeting or suggest_follow_up for next-step requests. "
        "Use log_interaction for new interaction notes and extraction-heavy messages.\n"
        f"Message: {state['message']}"
    )
    route = await groq_service.get_json_output(prompt, ROUTER_SCHEMA)
    planned_tools = _normalize_plan(route, state["message"])
    state["route"] = {"tools": planned_tools, "reason": route.get("reason", "") if isinstance(route, dict) else ""}
    return state


async def tool_executor_node(state: AgentState) -> AgentState:
    executed_tools: list[str] = []
    tool_results: list[dict] = []
    running_context = dict(state.get("context", {}))
    merged_form_updates: dict = {}

    for tool_name in state.get("route", {}).get("tools", [PRIMARY_FALLBACK]):
        tool = TOOL_REGISTRY[tool_name]
        if tool_name == "search_interactions":
            result = await tool(state["message"], running_context, state.get("db"))
        else:
            result = await tool(state["message"], running_context)
        executed_tools.append(tool_name)
        tool_results.append(result)
        form_updates = result.get("form_updates", {}) or {}
        running_context.update(form_updates)
        merged_form_updates.update(form_updates)

    state["context"] = running_context
    state["tool_results"] = tool_results
    state["executed_tools"] = executed_tools
    state["tool_result"] = tool_results[-1] if tool_results else {}
    state["route"]["form_updates"] = merged_form_updates
    return state


async def responder_node(state: AgentState) -> AgentState:
    tool_results = state.get("tool_results", [])
    responses = [result.get("response", "") for result in tool_results if result.get("response")]
    state["response"] = " ".join(responses) if responses else "Processed your request."
    return state


graph = StateGraph(AgentState)
graph.add_node("router_node", router_node)
graph.add_node("tool_executor_node", tool_executor_node)
graph.add_node("responder_node", responder_node)
graph.add_edge(START, "router_node")
graph.add_edge("router_node", "tool_executor_node")
graph.add_edge("tool_executor_node", "responder_node")
graph.add_edge("responder_node", END)
agent_graph = graph.compile()
