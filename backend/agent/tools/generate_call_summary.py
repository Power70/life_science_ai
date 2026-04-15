from services.groq_client import groq_service

NAME = "generate_call_summary"


async def run(message: str, context: dict) -> dict:
    prompt = f"Generate a concise professional call summary from this context: {context}"
    summary = await groq_service.get_completion(prompt, use_context_model=True)
    return {
        "tool_used": NAME,
        "tool_result": {"summary": summary},
        "form_updates": {"aiSummary": summary},
        "response": "Generated a professional call summary.",
    }
