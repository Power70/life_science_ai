from langgraph.graph import END, START, StateGraph

from agent.state import AgentState
from agent.tools import TOOL_REGISTRY
from services.groq_client import groq_service

ROUTER_SCHEMA = (
    '{"tools":["one of available tools"],"confidence":"0-1","reason":"string"}'
)
TOOLS_LIST = ", ".join(TOOL_REGISTRY.keys())
PRIMARY_FALLBACK = "log_interaction"


def _normalize_plan(route: dict, message: str) -> list[str]:
    planned_tools = route.get("tools") if isinstance(route, dict) else []
    if isinstance(planned_tools, str):
        planned_tools = [planned_tools]
    if not isinstance(planned_tools, list):
        planned_tools = []

    valid_tools: list[str] = []
    for tool_name in planned_tools:
        if tool_name in TOOL_REGISTRY and tool_name not in valid_tools:
            valid_tools.append(tool_name)

    message_lower = message.lower()

    # Keep fallback intent mapping lightweight and generic; rely on model routing
    # first, then apply broad intent fallback only when parsing/selection fails.
    has_schedule_intent = any(
        token in message_lower
        for token in ["schedule", "set up", "book", "arrange", "follow-up", "follow up"]
    )
    has_search_intent = any(
        token in message_lower for token in ["search", "find", "look up", "history"]
    )
    has_summary_intent = any(
        token in message_lower for token in ["summary", "summarize", "recap"]
    )
    has_suggestion_intent = any(
        token in message_lower
        for token in ["what should i do next", "next step", "next steps", "recommend"]
    )

    if not valid_tools:
        if has_schedule_intent:
            valid_tools = ["schedule_followup_meeting"]
        elif has_search_intent:
            valid_tools = ["search_interactions"]
        elif has_summary_intent:
            valid_tools = ["generate_call_summary"]
        elif has_suggestion_intent:
            valid_tools = ["suggest_follow_up"]
        else:
            valid_tools = [PRIMARY_FALLBACK]

    # Composite requests often ask for both recommendation and immediate scheduling.
    if (
        has_suggestion_intent
        and has_schedule_intent
        and "suggest_follow_up" not in valid_tools
    ):
        valid_tools.insert(0, "suggest_follow_up")

    # Keep scheduler before suggestion when user explicitly asks to schedule now.
    if has_schedule_intent and "schedule_followup_meeting" in valid_tools:
        valid_tools = [
            "schedule_followup_meeting",
            *[tool for tool in valid_tools if tool != "schedule_followup_meeting"],
        ]

    deduped_tools: list[str] = []
    for tool_name in valid_tools:
        if tool_name not in deduped_tools:
            deduped_tools.append(tool_name)

    return deduped_tools[:3]


async def router_node(state: AgentState) -> AgentState:
    prompt = (
        f"You are a routing planner for a pharma CRM AI assistant. Available tools: {TOOLS_LIST}. "
        "Choose the best ordered tools for the user request. "
        "Return STRICT JSON object only with keys: tools (array of tool names), confidence (0-1), reason (short string). "
        "Rules: "
        "(1) Prefer log_interaction for narrative interaction notes and field extraction. "
        "(2) Use edit_interaction only when user asks to modify existing form data. "
        "(3) Use search_interactions for retrieval/history questions. "
        "(4) Use suggest_follow_up for recommendation/what-next questions. "
        "(5) Use schedule_followup_meeting for explicit scheduling/task creation requests. "
        "(6) For compound requests, include multiple tools in execution order, max 3 tools. "
        f" Message: {state['message']}"
    )
    route = await groq_service.get_json_output(prompt, ROUTER_SCHEMA)
    planned_tools = _normalize_plan(route, state["message"])
    state["route"] = {
        "tools": planned_tools,
        "reason": route.get("reason", "") if isinstance(route, dict) else "",
    }
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
    responses = [
        result.get("response", "") for result in tool_results if result.get("response")
    ]
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
