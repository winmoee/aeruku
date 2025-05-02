from models.tool_definitions import ToolDefinition, ToolArgument

# ----- System tools -----
list_agents_tool = ToolDefinition(
    name="ListAgents",
    description="List available agents to interact with, pulled from goal_registry. ",
    arguments=[],
)

change_goal_tool = ToolDefinition(
    name="ChangeGoal",
    description="Change the goal of the active agent. ",
    arguments=[
        ToolArgument(
            name="goalID",
            type="string",
            description="Which goal to change to",
        ),
    ],
)

give_hint_tool = ToolDefinition(
    name="GiveHint",
    description="Give a hint to the user regarding the location of the pirate treasure. Use previous conversation to determine the hint_total, it should initially be 0 ",
    arguments=[
        ToolArgument(
            name="hint_total",
            type="number",
            description="How many hints have been given",
        ),
    ],
)
# ----- Sales Use Case Tools -----
search_leads_tool = ToolDefinition(
    name="SearchLeads",
    description="Search for potential leads based on a query string that can include industry, company size, location, or other criteria.",
    arguments=[
        ToolArgument(
            name="query",
            type="string",
            description="Search query describing the target leads (e.g., 'tech companies in San Francisco with 50-200 employees')",
        ),
    ],
)

save_leads_tool = ToolDefinition(
    name="SaveLeads",
    description="Save selected leads to the user's database for future reference.",
    arguments=[
        ToolArgument(
            name="lead_ids",
            type="string",
            description="Comma-separated IDs of leads to save, or 'all' to save all leads from the most recent search",
        ),
        ToolArgument(
            name="userConfirmation",
            type="string",
            description="Indication of user's desire to save the selected leads",
        ),
    ],
)

list_saved_leads_tool = ToolDefinition(
    name="ListSavedLeads",
    description="Retrieve the user's saved leads from their database.",
    arguments=[],
)

enrich_lead_tool = ToolDefinition(
    name="EnrichLead",
    description="Add additional information to a selected lead such as contact details, social profiles, or company information.",
    arguments=[
        ToolArgument(
            name="lead_id",
            type="string",
            description="ID of the lead to enrich",
        ),
    ],
)

get_enriched_lead_tool = ToolDefinition(
    name="GetEnrichedLead",
    description="Get detailed information about a specific lead that has been enriched.",
    arguments=[
        ToolArgument(
            name="lead_id",
            type="string",
            description="ID of the lead to retrieve enriched information for",
        ),
    ],
)

generate_email_tool = ToolDefinition(
    name="GenerateEmail",
    description="Create a personalized outreach email based on the lead's information and the user's product/service.",
    arguments=[
        ToolArgument(
            name="lead_name",
            type="string",
            description="Name of the lead contact person",
        ),
        ToolArgument(
            name="company_name",
            type="string",
            description="Name of the company",
        ),
        ToolArgument(
            name="title",
            type="string",
            description="Job title of the lead contact person",
        ),
        ToolArgument(
            name="product_description",
            type="string",
            description="Description of the user's product or service and value proposition",
        ),
    ],
)
