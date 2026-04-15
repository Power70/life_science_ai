from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from agent.graph import agent_graph
from app.database import get_db
from models import ChatMessage
from schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    user = ChatMessage(session_id=payload.session_id, role="user", content=payload.message)
    db.add(user)
    state = {
        "message": payload.message,
        "session_id": payload.session_id,
        "context": payload.context,
        "db": db,
        "route": {},
        "tool_result": {},
        "tool_results": [],
        "executed_tools": [],
        "response": "",
    }
    output = await agent_graph.ainvoke(state)
    result = output.get("tool_result", {})
    assistant = ChatMessage(
        session_id=payload.session_id,
        role="assistant",
        content=output.get("response", ""),
        tool_used=", ".join(output.get("executed_tools", [])) or result.get("tool_used"),
        tool_result=result.get("tool_result"),
    )
    db.add(assistant)
    await db.commit()
    return ChatResponse(
        response=output.get("response", ""),
        tool_used=", ".join(output.get("executed_tools", [])) or result.get("tool_used"),
        tool_result=result.get("tool_result"),
        tool_results=output.get("tool_results", []),
        form_updates=output.get("route", {}).get("form_updates", result.get("form_updates", {})),
    )
