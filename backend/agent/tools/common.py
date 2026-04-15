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
    prompt = (
        "Extract factual structured fields from this pharma CRM message. "
        "Use only values present or directly inferable from the message. "
        "Do not return placeholder words such as 'string', 'number', or 'null'. "
        "For missing fields return null, empty array, or empty string as appropriate.\n"
        f"Message:\n{message}"
    )
    raw = await groq_service.get_json_output(prompt, schema_hint)
    return _clean_placeholders(raw)


def _clean_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _clean_placeholders(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean_placeholders(v) for v in value]
    if isinstance(value, str) and value.strip().lower() in {"string", "number", "boolean", "null", "object", "array"}:
        return ""
    return value
