from services.groq_client import groq_service

NAME = "generate_call_summary"


async def run(message: str, context: dict) -> dict:
    prompt = (
        "Generate a concise professional call summary from this context. "
        "Return plain text only with no markdown syntax, no asterisks, no headings with **, and no bullet markers. "
        "Use simple labeled lines when needed (for example: Date:, Time:, Sentiment:, Next Steps:). "
        f"Context: {context}"
    )
    summary = await groq_service.get_completion(prompt, use_context_model=True)
    return {
        "tool_used": NAME,
        "tool_result": {"summary": summary},
        "form_updates": {"aiSummary": summary},
        "response": "Generated a professional call summary.",
    }
