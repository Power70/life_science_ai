from datetime import date
from typing import Any

from services.groq_client import groq_service


def merge_form_updates(context: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(context or {})
    merged.update({k: v for k, v in updates.items() if v is not None})
    if "date" not in merged:
        merged["date"] = str(date.today())
    return merged


async def llm_extract(message: str, schema_hint: str) -> dict:
    prompt = f"Extract structured fields from this pharma CRM message:\n{message}"
    return await groq_service.get_json_output(prompt, schema_hint)
