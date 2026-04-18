from datetime import date, timedelta

from agent.tools.common import llm_extract, merge_form_updates

NAME = "schedule_followup_meeting"


def _looks_relative_date_phrase(phrase: str) -> bool:
    text = phrase.lower().strip()
    if not text:
        return False
    relative_tokens = (
        "today",
        "tomorrow",
        "next",
        "this week",
        "next week",
        "in ",
    )
    day_tokens = (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    return any(token in text for token in relative_tokens) or any(
        day in text for day in day_tokens
    )


def _parse_relative_date(phrase: str) -> str:
    """Parse natural language date phrases like 'next Tuesday' or 'next week Tuesday'."""
    today = date.today()
    phrase_lower = phrase.lower().strip()

    if not phrase_lower:
        return ""

    if phrase_lower == "today":
        return today.strftime("%Y-%m-%d")
    if phrase_lower == "tomorrow":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # Handle weekday patterns with explicit semantics:
    # - "next Tuesday" => nearest upcoming Tuesday
    # - "next week Tuesday" => Tuesday in the next calendar week
    days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    for day_name, day_num in days.items():
        if f"next week {day_name}" in phrase_lower:
            # Find Monday of next calendar week, then move to target weekday.
            days_until_next_monday = (7 - today.weekday()) % 7
            if days_until_next_monday == 0:
                days_until_next_monday = 7
            next_week_monday = today + timedelta(days=days_until_next_monday)
            target_date = next_week_monday + timedelta(days=day_num)
            return target_date.strftime("%Y-%m-%d")

        if f"this week {day_name}" in phrase_lower:
            start_of_week = today - timedelta(days=today.weekday())
            target_date = start_of_week + timedelta(days=day_num)
            if target_date < today:
                target_date = target_date + timedelta(days=7)
            return target_date.strftime("%Y-%m-%d")

        if f"next {day_name}" in phrase_lower:
            # Find the nearest upcoming occurrence of that weekday.
            days_ahead = (day_num - today.weekday()) % 7
            if days_ahead <= 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime("%Y-%m-%d")

        if day_name in phrase_lower:
            # Bare weekday (e.g., "Tuesday") defaults to nearest upcoming weekday.
            days_ahead = (day_num - today.weekday()) % 7
            if days_ahead < 0:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
            if target_date < today:
                target_date = target_date + timedelta(days=7)
            return target_date.strftime("%Y-%m-%d")

    # Handle "in X days/weeks" patterns.
    if "in " in phrase_lower:
        if " day" in phrase_lower:
            try:
                num_days = int(phrase_lower.split("in ")[1].split(" ")[0])
                target_date = today + timedelta(days=num_days)
                return target_date.strftime("%Y-%m-%d")
            except (ValueError, IndexError):
                pass
        if " week" in phrase_lower:
            try:
                num_weeks = int(phrase_lower.split("in ")[1].split(" ")[0])
                target_date = today + timedelta(weeks=num_weeks)
                return target_date.strftime("%Y-%m-%d")
            except (ValueError, IndexError):
                pass

    return ""


def _is_past_date(date_str: str) -> bool:
    try:
        parsed = date.fromisoformat(date_str)
        return parsed < date.today()
    except ValueError:
        return True


async def run(message: str, context: dict) -> dict:
    today_str = date.today().strftime("%Y-%m-%d")
    extraction_message = (
        f"Today's date is {today_str}. Convert relative dates from the user request into exact "
        "YYYY-MM-DD values. Interpret 'next week Tuesday' as Tuesday in the next calendar "
        "week, and 'next Tuesday' as the nearest upcoming Tuesday. User request: "
        f"{message}"
    )
    data = await llm_extract(
        extraction_message,
        '{"action":"string (the follow-up task to schedule)","dueDate":"YYYY-MM-DD or null","time":"HH:MM or null","raw_date_text":"the user\'s original phrasing of when (e.g., \'next Tuesday\', \'in 2 weeks\')"}',
    )

    action_text = str(data.get("action") or "").strip()
    due_date = str(data.get("dueDate") or "").strip()
    due_time = str(data.get("time") or "").strip()
    raw_date_text = str(data.get("raw_date_text") or "").strip().lower()

    # Resolve relative phrases deterministically and reject invalid/past dates.
    if _looks_relative_date_phrase(raw_date_text):
        parsed_relative = _parse_relative_date(raw_date_text)
        if parsed_relative:
            due_date = parsed_relative

    if (
        not due_date
        or due_date == "null"
        or _is_invalid_year(due_date)
        or _is_past_date(due_date)
    ):
        parsed_date = _parse_relative_date(raw_date_text)
        if parsed_date:
            due_date = parsed_date
        else:
            due_date = ""

    # Combine action with time if present.
    if due_time and due_time not in {"null", ""}:
        action_text = f"{action_text} at {due_time}"

    action_item = {
        "action": action_text or "Follow up with HCP",
        "dueDate": due_date,
    }

    existing = list(context.get("followUpActions", []))
    existing.append(action_item)
    form_updates = merge_form_updates(
        context, {"followUpActions": existing}, lock_timestamp=False
    )
    return {
        "tool_used": NAME,
        "tool_result": action_item,
        "form_updates": form_updates,
        "response": "Scheduled a follow-up action from your request.",
    }


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
