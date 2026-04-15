from langgraph.graph import END, START, StateGraph

from agent.state import AgentState
from agent.tools import TOOL_REGISTRY
from services.groq_client import groq_service

ROUTER_SCHEMA = '{"tool":"one of available tools","confidence":"0-1","reason":"string"}'
TOOLS_LIST = ", ".join(TOOL_REGISTRY.keys())


async def router_node(state: AgentState) -> AgentState:
    prompt = (
        f"Pick the best tool for this message. Tools: {TOOLS_LIST}. "
        "Always choose one tool. Use suggest_follow_up for requests about next steps/recommendations. "
        "Use edit_interaction for corrections to existing form data. "
        "Use log_interaction for new interaction notes.\n"
        f"Message: {state['message']}"
    )
    route = await groq_service.get_json_output(prompt, ROUTER_SCHEMA)
    state["route"] = (
        route if route.get("tool") in TOOL_REGISTRY else {"tool": "log_interaction"}
    )
    return state


async def tool_executor_node(state: AgentState) -> AgentState:
    tool_name = state["route"]["tool"]
    tool = TOOL_REGISTRY[tool_name]
    state["tool_result"] = await tool(state["message"], state.get("context", {}))
    return state


async def responder_node(state: AgentState) -> AgentState:
    result = state.get("tool_result", {})
    state["response"] = result.get("response", "Processed your request.")
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
