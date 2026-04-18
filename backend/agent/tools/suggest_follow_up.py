from datetime import date, timedelta

from agent.tools.common import llm_extract, merge_form_updates

NAME = "suggest_follow_up"


def _is_invalid_year(date_str: str) -> bool:
    """Check if a YYYY-MM-DD date string has an invalid or outdated year."""
    try:
        parts = date_str.split("-")
        if len(parts) != 3:
            return True
        year = int(parts[0])
        current_year = date.today().year
        # Flag dates in the past or more than 2 years in future as invalid.
        return year < current_year or year > current_year + 2
    except (ValueError, IndexError):
        return True


def _fix_year_in_date(date_str: str) -> str:
    """If a date has an invalid year, shift it to the current year."""
    if not date_str or not _is_invalid_year(date_str):
        return date_str
    try:
        parts = date_str.split("-")
        if len(parts) == 3:
            # Replace year with current year.
            current_year = date.today().year
            return f"{current_year}-{parts[1]}-{parts[2]}"
    except (ValueError, IndexError):
        pass
    return date_str


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(
        message,
        '{"actions":[{"action":"string","rationale":"string","dueDate":"YYYY-MM-DD or null"}]}',
    )

    # Fix any invalid years in suggested follow-up dates.
    actions = data.get("actions", [])
    for action in actions:
        if "dueDate" in action and action["dueDate"]:
            action["dueDate"] = _fix_year_in_date(action["dueDate"])

    form_updates = merge_form_updates(
        context, {"aiSuggestedFollowUps": actions}, lock_timestamp=True
    )
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": form_updates,
        "response": "Generated AI follow-up recommendations.",
    }
