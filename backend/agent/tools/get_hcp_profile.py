NAME = "get_hcp_profile"


async def run(message: str, context: dict) -> dict:
    hcp = context.get("hcp", "Selected HCP")
    result = {"hcp": hcp, "summary": "Profile lookup is context-aware and ready for DB enrichment."}
    return {
        "tool_used": NAME,
        "tool_result": result,
        "form_updates": {},
        "response": f"Fetched profile context for {hcp}.",
    }
