from agent.tools.common import llm_extract

NAME = "distribute_sample"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(message, '{"product":"string","dosage":"string","quantity":"number","lotNumber":"string"}')
    existing = list(context.get("samplesDistributed", []))
    existing.append(data)
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": {"samplesDistributed": existing},
        "response": "Added sample distribution details to the form.",
    }
