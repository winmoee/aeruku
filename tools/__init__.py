from .search_leads import search_leads
from .enrich_lead import enrich_lead
from .generate_email import generate_email

def get_handler(tool_name: str):
    if tool_name == "SearchLeads":
        return search_leads
    if tool_name == "EnrichLead":
        return enrich_lead
    if tool_name == "GenerateEmail":
        return generate_email

    raise ValueError(f"Unknown tool: {tool_name}")
