from .search_leads import search_leads
from .enrich_lead import enrich_lead
from .generate_email import generate_email
from .draft_email import draft_email 
from .list_agents import list_agents
from .change_goal import change_goal



def get_handler(tool_name: str):
    if tool_name == "SearchLeads":
        return search_leads
    if tool_name == "EnrichLead":
        return enrich_lead
    if tool_name == "GenerateEmail":
        return generate_email
    if tool_name == "DraftEmail":  
        return draft_email
    if tool_name == "ListAgents":
        return list_agents
    if tool_name == "ChangeGoal":
        return change_goal

    raise ValueError(f"Unknown tool: {tool_name}")