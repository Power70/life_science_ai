from agent.tools.analyze_sentiment import run as analyze_sentiment
from agent.tools.distribute_sample import run as distribute_sample
from agent.tools.edit_interaction import run as edit_interaction
from agent.tools.generate_call_summary import run as generate_call_summary
from agent.tools.get_hcp_profile import run as get_hcp_profile
from agent.tools.log_interaction import run as log_interaction
from agent.tools.schedule_followup_meeting import run as schedule_followup_meeting
from agent.tools.search_interactions import run as search_interactions
from agent.tools.share_material import run as share_material
from agent.tools.suggest_follow_up import run as suggest_follow_up

TOOL_REGISTRY = {
    "log_interaction": log_interaction,
    "edit_interaction": edit_interaction,
    "get_hcp_profile": get_hcp_profile,
    "suggest_follow_up": suggest_follow_up,
    "analyze_sentiment": analyze_sentiment,
    "search_interactions": search_interactions,
    "distribute_sample": distribute_sample,
    "share_material": share_material,
    "generate_call_summary": generate_call_summary,
    "schedule_followup_meeting": schedule_followup_meeting,
}
