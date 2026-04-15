from datetime import date, timedelta
from typing import Any

from sqlalchemy import Text, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from agent.tools.common import llm_extract
from models import HCP, Interaction

NAME = "search_interactions"


async def run(message: str, context: dict, db: AsyncSession | None = None) -> dict:
    data = await llm_extract(
        message,
        '{"hcp":"doctor name or null","product":"product name or null","topic":"topic or null","timeframe":"last week|last month|custom|today|null","notes":"string or null"}',
    )

    if db is None:
        result = {"query": message, "parsed": data, "results": []}
        return {
            "tool_used": NAME,
            "tool_result": result,
            "form_updates": {},
            "response": "I parsed your search request, but the database session is unavailable in this environment.",
        }

    hcp_name = (data.get("hcp") or context.get("hcp") or "").strip()
    product = (data.get("product") or "").strip()
    topic = (data.get("topic") or "").strip()

    cutoff = date.today() - timedelta(days=30)
    stmt = select(Interaction, HCP).outerjoin(HCP, Interaction.hcp_id == HCP.id)
    stmt = stmt.where(Interaction.interaction_date >= cutoff)

    if hcp_name:
        pattern = f"%{hcp_name.lower()}%"
        stmt = stmt.where(func.lower(HCP.full_name).like(pattern))

    if product or topic:
        search_terms = [term for term in [product, topic] if term]
        search_term = search_terms[0]
        combined_text = func.lower(
            func.concat(
                func.coalesce(Interaction.topics_discussed, ""),
                " ",
                func.coalesce(Interaction.outcomes, ""),
                " ",
                func.coalesce(Interaction.raw_chat_input, ""),
                " ",
                cast(Interaction.materials_shared, Text),
                " ",
                cast(Interaction.samples_distributed, Text),
                " ",
                func.coalesce(Interaction.ai_summary, ""),
            )
        )
        stmt = stmt.where(combined_text.like(f"%{search_term.lower()}%"))

    stmt = stmt.order_by(
        Interaction.interaction_date.desc(), Interaction.created_at.desc()
    ).limit(10)
    rows = (await db.execute(stmt)).all()

    results: list[dict[str, Any]] = []
    for interaction, hcp in rows:
        results.append(
            {
                "id": str(interaction.id),
                "hcp": hcp.full_name if hcp else None,
                "date": interaction.interaction_date.isoformat(),
                "time": interaction.interaction_time.isoformat()
                if interaction.interaction_time
                else None,
                "topicsDiscussed": interaction.topics_discussed,
                "sentiment": interaction.sentiment,
                "outcomes": interaction.outcomes,
                "aiSummary": interaction.ai_summary,
            }
        )

    result = {"query": message, "parsed": data, "results": results}
    if results:
        summary = f"Found {len(results)} related interaction(s) in the last month."
    else:
        summary = "I couldn't find a matching interaction in the last month."

    return {
        "tool_used": NAME,
        "tool_result": result,
        "form_updates": {},
        "response": summary,
    }
