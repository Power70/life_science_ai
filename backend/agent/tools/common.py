from datetime import date, datetime
from typing import Any

from services.groq_client import groq_service


KEY_ALIASES = {
    "hcp_name": "hcp",
    "interaction_type": "interactionType",
    "interaction_date": "date",
    "interaction_time": "time",
    "topics_discussed": "topicsDiscussed",
    "materials_shared": "materialsShared",
    "samples_distributed": "samplesDistributed",
    "follow_up_actions": "followUpActions",
    "followupActions": "followUpActions",
    "followups": "followUpActions",
    "outcome": "outcomes",
    "key_outcomes": "outcomes",
    "ai_suggested_followups": "aiSuggestedFollowUps",
    "ai_suggested_follow_ups": "aiSuggestedFollowUps",
    "suggested_follow_ups": "aiSuggestedFollowUps",
}


def normalize_form_updates(updates: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for raw_key, raw_value in (updates or {}).items():
        key = KEY_ALIASES.get(raw_key, raw_key)
        normalized[key] = raw_value

    # Accept textual follow-up values and convert to structured objects used by the UI.
    followups = normalized.get("followUpActions")
    if isinstance(followups, str) and followups.strip():
        normalized["followUpActions"] = [{"action": followups.strip()}]
    elif isinstance(followups, list):
        converted = []
        for item in followups:
            if isinstance(item, str) and item.strip():
                converted.append({"action": item.strip()})
            elif isinstance(item, dict):
                converted.append(item)
        normalized["followUpActions"] = converted

    ai_suggested = normalized.get("aiSuggestedFollowUps")
    if isinstance(ai_suggested, str) and ai_suggested.strip():
        normalized["aiSuggestedFollowUps"] = [{"action": ai_suggested.strip()}]
    elif isinstance(ai_suggested, list):
        converted = []
        for item in ai_suggested:
            if isinstance(item, str) and item.strip():
                converted.append({"action": item.strip()})
            elif isinstance(item, dict):
                converted.append(item)
        normalized["aiSuggestedFollowUps"] = converted

    return normalized


def _is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def merge_form_updates(
    context: dict[str, Any], updates: dict[str, Any], lock_timestamp: bool = False
) -> dict[str, Any]:
    merged = dict(context or {})
    normalized = normalize_form_updates(updates or {})
    merged.update({k: v for k, v in normalized.items() if _is_meaningful(v)})

    if lock_timestamp:
        merged["date"] = str(date.today())
        merged["time"] = datetime.now().strftime("%H:%M")
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
    if isinstance(value, str) and value.strip().lower() in {
        "string",
        "number",
        "boolean",
        "null",
        "object",
        "array",
    }:
        return ""
    return value
