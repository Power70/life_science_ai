import json

from langchain_groq import ChatGroq

from app.config import settings


class GroqService:
    def __init__(self) -> None:
        self.enabled = bool(settings.groq_api_key)
        self.primary = None
        self.context = None
        self.primary_model_name = settings.groq_primary_model
        self.context_model_name = settings.groq_context_model
        if self.enabled:
            self.primary = ChatGroq(
                model_name=self.primary_model_name,
                groq_api_key=settings.groq_api_key,
                temperature=0.2,
                max_tokens=1024,
            )
            self.context = ChatGroq(
                model_name=self.context_model_name,
                groq_api_key=settings.groq_api_key,
                temperature=0.3,
                max_tokens=2048,
            )

    def _build_model(self, model_name: str, use_context_settings: bool) -> ChatGroq:
        return ChatGroq(
            model_name=model_name,
            groq_api_key=settings.groq_api_key,
            temperature=0.3 if use_context_settings else 0.2,
            max_tokens=2048 if use_context_settings else 1024,
        )

    async def get_completion(self, prompt: str, use_context_model: bool = False) -> str:
        if not self.enabled:
            return "LLM unavailable in this environment. Configure GROQ_API_KEY in backend/.env."
        model = self.context if use_context_model else self.primary
        try:
            result = await model.ainvoke(prompt)
        except Exception as exc:
            # Handle model decommissioning gracefully by retrying with the context model.
            if "model_decommissioned" in str(exc) and not use_context_model and self.context is not None:
                result = await self.context.ainvoke(prompt)
            else:
                raise
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
