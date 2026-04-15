import json

from langchain_groq import ChatGroq

from app.config import settings

PRIMARY_MODEL = "gemma2-9b-it"
CONTEXT_MODEL = "llama-3.3-70b-versatile"


class GroqService:
    def __init__(self) -> None:
        self.enabled = bool(settings.groq_api_key)
        self.primary = None
        self.context = None
        if self.enabled:
            self.primary = ChatGroq(
                model_name=PRIMARY_MODEL,
                groq_api_key=settings.groq_api_key,
                temperature=0.2,
                max_tokens=1024,
            )
            self.context = ChatGroq(
                model_name=CONTEXT_MODEL,
                groq_api_key=settings.groq_api_key,
                temperature=0.3,
                max_tokens=2048,
            )

    async def get_completion(self, prompt: str, use_context_model: bool = False) -> str:
        if not self.enabled:
            return "LLM unavailable in this environment. Configure GROQ_API_KEY in backend/.env."
        model = self.context if use_context_model else self.primary
        result = await model.ainvoke(prompt)
        return result.content if isinstance(result.content, str) else str(result.content)

    async def get_json_output(self, prompt: str, schema_hint: str, use_context_model: bool = False) -> dict:
        strict_prompt = (
            f"{prompt}\n\nSchema:\n{schema_hint}\n"
            "Return only valid JSON. No markdown fences and no explanations."
        )
        raw = await self.get_completion(strict_prompt, use_context_model=use_context_model)
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            return {}
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return {}


groq_service = GroqService()
