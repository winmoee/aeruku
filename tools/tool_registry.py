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

enrich_lead_tool = ToolDefinition(
    name="EnrichLead",
    description="Enrich LinkedIn profiles with additional information using the MCP server's LinkedIn Profile Scraper.",
    arguments=[
        ToolArgument(
            name="profileUrls",
            type="array",
            description="Array of LinkedIn profile URLs to enrich",
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

draft_email_tool = ToolDefinition(
    name="DraftEmail",
    description="Draft a custom email to a lead. Allows the user to specify the recipient, subject, and body of the email.",
    arguments=[
        ToolArgument(
            name="recipient_email",
            type="string",
            description="Email address of the recipient",
        ),
        ToolArgument(
            name="subject",
            type="string",
            description="Subject line of the email",
        ),
        ToolArgument(
            name="body",
            type="string",
            description="Main content of the email",
        ),
    ],
)
