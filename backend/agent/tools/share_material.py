from agent.tools.common import llm_extract

NAME = "share_material"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(message, '{"name":"string","type":"Brochure|Study|PDF|Flyer|Poster","quantity":"number"}')
    existing = list(context.get("materialsShared", []))
    existing.append(data)
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": {"materialsShared": existing},
        "response": "Added shared material details to the form.",
    }
