import os
from typing import List
from models.tool_definitions import AgentGoal
import tools.tool_registry as tool_registry

# Turn on Silly Mode - this should be a description of the persona you'd like the bot to have and can be a single word or a phrase.
# Example if you want the bot to be a specific person, like Mario or Christopher Walken, or to describe a specific tone:
# SILLY_MODE="Christopher Walken"
# SILLY_MODE="belligerent"
#
# Example if you want it to take on a persona (include 'a'):
# SILLY_MODE="a pirate"
# Note - this only works with certain LLMs. Grok for sure will stay in character, while OpenAI will not.
SILLY_MODE = "off"
if SILLY_MODE is not None and SILLY_MODE != "off":
    silly_prompt = "You are " + SILLY_MODE + ", stay in character at all times. "
    print("Silly mode is on: " + SILLY_MODE)
else:
    silly_prompt = ""

starter_prompt_generic = (
    silly_prompt
    + "Welcome me, give me a description of what you can do, then ask me for the details you need to do your job."
)

goal_choose_agent_type = AgentGoal(
    id="goal_choose_agent_type",
    category_tag="agent_selection",
    agent_name="Choose Agent",
    agent_friendly_description="Choose the type of agent to assist you today. You can always interrupt an existing agent to pick a new one.",
    tools=[
        tool_registry.list_agents_tool,
        tool_registry.change_goal_tool,
    ],
    description="The user wants to choose which type of agent they will interact with. "
    "Help the user select an agent by gathering args for the Changegoal tool, in order: "
    "1. ListAgents: List agents available to interact with. Do not ask for user confirmation for this tool. "
    "2. ChangeGoal: Change goal of agent "
    "After these tools are complete, change your goal to the new goal as chosen by the user. "
    "The available agents include: Find Leads (for finding potential sales leads based on criteria), "
    "Enrich Leads (for enhancing existing leads with additional information), "
    "Generate Emails (for creating personalized outreach emails), and "
    "Draft Email (for creating custom emails with specific content).",
    starter_prompt=silly_prompt
    + "Welcome me, give me a description of what you can do, then ask me for the details you need to do your job. List all details of all agents as provided by the output of the first tool included in this goal. ",
    example_conversation_history="\n ".join(
    [
        "agent: Here are the currently available agents.",
        "tool_result: { agents: 'agent_name': 'Find Leads', 'goal_id': 'goal_find_leads', 'agent_description': 'Find potential leads based on your target criteria.',"
        "'agent_name': 'Enrich Leads', 'goal_id': 'goal_enrich_leads', 'agent_description': 'Enhance your existing leads with additional contact information and details.',"
        "'agent_name': 'Generate Emails', 'goal_id': 'goal_generate_emails', 'agent_description': 'Create personalized outreach emails for your leads.',"
        "'agent_name': 'Draft Email', 'goal_id': 'goal_draft_email', 'agent_description': 'Create custom emails to send to your leads with specific content.' }",
        "agent: The available agents are: Find Leads, Enrich Leads, Generate Emails, and Draft Email. \n Which agent would you like to work with?",
        "user: I'd like to find some potential sales leads for my business using the Find Leads agent",
        "user_confirmed_tool_run: <user clicks confirm on ChangeGoal tool>",
        "tool_result: { 'new_goal': 'goal_find_leads' }",
    ]
),

)


# ----- Sales Goals ---
goal_find_leads = AgentGoal(
    id="goal_find_leads",
    category_tag="sales",
    agent_name="Find Leads",
    agent_friendly_description="Find potential leads based on your target criteria.",
    tools=[
        tool_registry.search_leads_tool,
    ],
    description="The user wants to find potential sales leads based on specific criteria. "
    "Help the user gather args for these tools in order: "
    "1. SearchLeads: Search for potential leads based on industry, company size, location, or other criteria ",
    starter_prompt=starter_prompt_generic,
    example_conversation_history="\n ".join(
        [
            "user: I need to find some new sales leads",
            "agent: I'd be happy to help you find new sales leads! To get started, I'll need some information about your target audience. Could you tell me what industry, company size, location, or other criteria you're looking for?",
            "user: I'm looking for tech companies in San Francisco with 50-200 employees",
            "agent: Great! Let me search for tech companies in San Francisco with 50-200 employees.",
            "user_confirmed_tool_run: <user clicks confirm on SearchLeads tool>",
            "tool_result: { 'leads': [{'company_name': 'TechStart Inc.', 'industry': 'Software', 'location': 'San Francisco, CA', 'size': '120 employees', 'website': 'techstart.com'}, {'company_name': 'DataFlow Systems', 'industry': 'Data Analytics', 'location': 'San Francisco, CA', 'size': '85 employees', 'website': 'dataflowsys.com'}, {'company_name': 'CloudNine Solutions', 'industry': 'Cloud Computing', 'location': 'San Francisco, CA', 'size': '175 employees', 'website': 'cloudninesol.com'}] }",
            "agent: I found 3 leads that match your criteria:\n\n1. TechStart Inc.\n   - Industry: Software\n   - Location: San Francisco, CA\n   - Size: 120 employees\n   - Website: techstart.com\n\n2. DataFlow Systems\n   - Industry: Data Analytics\n   - Location: San Francisco, CA\n   - Size: 85 employees\n   - Website: dataflowsys.com\n\n3. CloudNine Solutions\n   - Industry: Cloud Computing\n   - Location: San Francisco, CA\n   - Size: 175 employees\n   - Website: cloudninesol.com\n\nWould you like to save these leads to your database?",
            "user: Yes, save all of them",
            "user_confirmed_tool_run: <user clicks confirm on SaveLeads tool>",
            "tool_result: { 'status': 'success', 'saved_count': 3, 'message': 'Successfully saved 3 leads to your database.' }",
            "agent: Great! I've successfully saved all 3 leads to your database. Is there anything else you'd like to know about these companies or would you like to search for additional leads with different criteria?",
        ]
    ),
)

goal_enrich_leads = AgentGoal(
    id="goal_enrich_leads",
    category_tag="sales",
    agent_name="Enrich Leads",
    agent_friendly_description="Enhance your existing leads with additional contact information and details.",
    tools=[
        tool_registry.enrich_lead_tool,
    ],
    description="The user wants to enrich their existing leads with additional information. "
    "Help the user gather args for these tools in order: "
    "1. EnrichLead: Add additional information to selected leads such as contact details, social profiles, or company information ",
    starter_prompt=starter_prompt_generic,
    example_conversation_history="\n ".join(
        [
            "user: I need to get more information about my leads",
            "agent: I'd be happy to help you enrich your leads with additional information. First, let's retrieve your saved leads from the database.",
            "user_confirmed_tool_run: <user clicks confirm on ListSavedLeads tool>",
            "tool_result: { 'leads': [{'id': '1', 'company_name': 'TechStart Inc.', 'industry': 'Software', 'location': 'San Francisco, CA', 'size': '120 employees', 'website': 'techstart.com'}, {'id': '2', 'company_name': 'DataFlow Systems', 'industry': 'Data Analytics', 'location': 'San Francisco, CA', 'size': '85 employees', 'website': 'dataflowsys.com'}, {'id': '3', 'company_name': 'CloudNine Solutions', 'industry': 'Cloud Computing', 'location': 'San Francisco, CA', 'size': '175 employees', 'website': 'cloudninesol.com'}] }",
            "agent: I found 3 leads in your database:\n\n1. TechStart Inc. (ID: 1)\n   - Industry: Software\n   - Location: San Francisco, CA\n   - Size: 120 employees\n   - Website: techstart.com\n\n2. DataFlow Systems (ID: 2)\n   - Industry: Data Analytics\n   - Location: San Francisco, CA\n   - Size: 85 employees\n   - Website: dataflowsys.com\n\n3. CloudNine Solutions (ID: 3)\n   - Industry: Cloud Computing\n   - Location: San Francisco, CA\n   - Size: 175 employees\n   - Website: cloudninesol.com\n\nWhich lead would you like to enrich with additional information?",
            "user: Let's enrich TechStart Inc.",
            "user_confirmed_tool_run: <user clicks confirm on EnrichLead tool>",
            "tool_result: { 'lead_id': '1', 'enriched_data': {'company_name': 'TechStart Inc.', 'industry': 'Software', 'location': 'San Francisco, CA', 'size': '120 employees', 'website': 'techstart.com', 'founded': '2018', 'key_people': [{'name': 'Sarah Johnson', 'title': 'CEO', 'email': 'sarah.johnson@techstart.com', 'linkedin': 'linkedin.com/in/sarahjohnson'}, {'name': 'Michael Chen', 'title': 'CTO', 'email': 'michael.chen@techstart.com', 'linkedin': 'linkedin.com/in/michaelchen'}], 'funding': '$12M Series A', 'technologies': ['React', 'Node.js', 'AWS'], 'competitors': ['CodeCraft', 'DevSphere']} }",
            "agent: I've successfully enriched the information for TechStart Inc. Here's what I found:\n\n**TechStart Inc.**\n- Founded: 2018\n- Funding: $12M Series A\n- Technologies: React, Node.js, AWS\n- Competitors: CodeCraft, DevSphere\n\n**Key People:**\n1. Sarah Johnson - CEO\n   - Email: sarah.johnson@techstart.com\n   - LinkedIn: linkedin.com/in/sarahjohnson\n\n2. Michael Chen - CTO\n   - Email: michael.chen@techstart.com\n   - LinkedIn: linkedin.com/in/michaelchen\n\nWould you like to enrich any other leads?",
        ]
    ),
)

goal_generate_emails = AgentGoal(
    id="goal_generate_emails",
    category_tag="sales",
    agent_name="Generate Emails",
    agent_friendly_description="Create personalized outreach emails for your leads.",
    tools=[
        tool_registry.generate_email_tool,
    ],
    description="The user wants to generate personalized outreach emails for their leads. "
    "Help the user gather args for these tools in order: "
    "1. GetEnrichedLead: Get detailed information about a specific lead "
    "2. GenerateEmail: Create a personalized outreach email based on the lead's information and the user's product/service ",
    starter_prompt=starter_prompt_generic,
    example_conversation_history="\n ".join(
        [
            "user: I need to create some outreach emails for my leads",
            "agent: I'd be happy to help you generate personalized outreach emails for your leads. First, let's retrieve your saved leads from the database.",
            "user_confirmed_tool_run: <user clicks confirm on ListSavedLeads tool>",
            "tool_result: { 'leads': [{'id': '1', 'company_name': 'TechStart Inc.', 'industry': 'Software', 'location': 'San Francisco, CA', 'size': '120 employees', 'website': 'techstart.com'}, {'id': '2', 'company_name': 'DataFlow Systems', 'industry': 'Data Analytics', 'location': 'San Francisco, CA', 'size': '85 employees', 'website': 'dataflowsys.com'}, {'id': '3', 'company_name': 'CloudNine Solutions', 'industry': 'Cloud Computing', 'location': 'San Francisco, CA', 'size': '175 employees', 'website': 'cloudninesol.com'}] }",
            "agent: I found 3 leads in your database:\n\n1. TechStart Inc. (ID: 1)\n   - Industry: Software\n   - Location: San Francisco, CA\n   - Size: 120 employees\n   - Website: techstart.com\n\n2. DataFlow Systems (ID: 2)\n   - Industry: Data Analytics\n   - Location: San Francisco, CA\n   - Size: 85 employees\n   - Website: dataflowsys.com\n\n3. CloudNine Solutions (ID: 3)\n   - Industry: Cloud Computing\n   - Location: San Francisco, CA\n   - Size: 175 employees\n   - Website: cloudninesol.com\n\nWhich lead would you like to create an outreach email for?",
            "user: Let's create an email for TechStart Inc.",
            "user_confirmed_tool_run: <user clicks confirm on GetEnrichedLead tool>",
            "tool_result: { 'lead_id': '1', 'enriched_data': {'company_name': 'TechStart Inc.', 'industry': 'Software', 'location': 'San Francisco, CA', 'size': '120 employees', 'website': 'techstart.com', 'founded': '2018', 'key_people': [{'name': 'Sarah Johnson', 'title': 'CEO', 'email': 'sarah.johnson@techstart.com', 'linkedin': 'linkedin.com/in/sarahjohnson'}, {'name': 'Michael Chen', 'title': 'CTO', 'email': 'michael.chen@techstart.com', 'linkedin': 'linkedin.com/in/michaelchen'}], 'funding': '$12M Series A', 'technologies': ['React', 'Node.js', 'AWS'], 'competitors': ['CodeCraft', 'DevSphere']} }",
            "agent: I've retrieved the enriched information for TechStart Inc. Now, to create a personalized outreach email, could you tell me about your product or service and what specific value proposition you'd like to highlight for this company?",
            "user: We offer a cybersecurity solution for startups that helps protect their cloud infrastructure. Our solution is particularly good for companies using AWS.",
            "user_confirmed_tool_run: <user clicks confirm on GenerateEmail tool>",
            "tool_result: { 'recipient': {'name': 'Sarah Johnson', 'title': 'CEO', 'email': 'sarah.johnson@techstart.com'}, 'subject': 'Protecting TechStart's AWS Infrastructure: A Tailored Security Solution', 'body': 'Hi Sarah,\\n\\nI noticed that TechStart has been making waves in the software industry since your founding in 2018, and congratulations on your recent $12M Series A funding!\\n\\nAs you scale your AWS infrastructure, security challenges often grow exponentially. Our cybersecurity solution has helped similar startups like yours prevent data breaches while maintaining the agility needed for rapid growth.\\n\\nGiven your team's focus on React and Node.js development on AWS, I'd love to share how our platform specifically addresses the unique security challenges in this tech stack.\\n\\nWould you be open to a 15-minute call next week to discuss how we've helped companies similar to TechStart reduce security incidents by 73% while cutting compliance overhead in half?\\n\\nBest regards,\\n[Your Name]', 'notes': 'Personalization points: Recent funding, specific tech stack (AWS), company age (founded 2018), appropriate decision-maker (CEO for strategic security decisions)' }",
            "agent: I've created a personalized outreach email for Sarah Johnson, CEO of TechStart Inc. Here it is:\n\n**Subject:** Protecting TechStart's AWS Infrastructure: A Tailored Security Solution\n\n**Email:**\nHi Sarah,\n\nI noticed that TechStart has been making waves in the software industry since your founding in 2018, and congratulations on your recent $12M Series A funding!\n\nAs you scale your AWS infrastructure, security challenges often grow exponentially. Our cybersecurity solution has helped similar startups like yours prevent data breaches while maintaining the agility needed for rapid growth.\n\nGiven your team's focus on React and Node.js development on AWS, I'd love to share how our platform specifically addresses the unique security challenges in this tech stack.\n\nWould you be open to a 15-minute call next week to discuss how we've helped companies similar to TechStart reduce security incidents by 73% while cutting compliance overhead in half?\n\nBest regards,\n[Your Name]\n\n**Personalization Notes:**\n- Referenced their recent Series A funding\n- Mentioned their specific tech stack (AWS)\n- Acknowledged the company's founding year (2018)\n- Addressed the appropriate decision-maker (CEO for strategic security decisions)\n\nWould you like to make any changes to this email or create an outreach email for another lead?",
        ]
    ),
)

goal_draft_email = AgentGoal(
    id="goal_draft_email",
    category_tag="sales",
    agent_name="Draft Email",
    agent_friendly_description="Create custom emails to send to your leads with specific content.",
    tools=[
        tool_registry.draft_email_tool,
    ],
    description="The user wants to draft a custom email to a lead. "
    "Help the user gather args for the DraftEmail tool: "
    "1. DraftEmail: Create a custom email with specified recipient, subject, and body content.",
    starter_prompt=starter_prompt_generic,
    example_conversation_history="\n ".join(
        [
            "user: I need to write a custom email to a lead",
            "agent: I'd be happy to help you draft a custom email. Could you please provide the recipient's email address, the subject line, and the content you'd like to include in the email?",
            "user: The email is for sarah.johnson@techstart.com. The subject should be 'Following up on our conversation'. I want to thank her for the meeting yesterday and confirm our next steps.",
            "agent: I'll help you draft that email. Let me confirm the details:\n\n- Recipient: sarah.johnson@techstart.com\n- Subject: Following up on our conversation\n- Content: Thank Sarah for the meeting yesterday and confirm next steps\n\nIs that correct? Would you like to add any specific details about the next steps or other points you discussed?",
            "user: Yes, please mention that I'll send the proposal by Friday and that I look forward to our call next Tuesday at 2pm.",
            "user_confirmed_tool_run: <user clicks confirm on DraftEmail tool>",
            "tool_result: { 'status': 'success', 'recipient': 'sarah.johnson@techstart.com', 'subject': 'Following up on our conversation', 'body': 'Hi Sarah,\\n\\nThank you for taking the time to meet with me yesterday. I appreciated the opportunity to discuss how our services could benefit TechStart.\\n\\nAs promised, I will send over the detailed proposal by Friday for your review.\\n\\nI'm looking forward to our follow-up call next Tuesday at 2pm to address any questions you might have and discuss potential next steps.\\n\\nPlease let me know if you need any additional information in the meantime.\\n\\nBest regards,\\n[Your Name]' }",
            "agent: I've drafted your email to Sarah Johnson. Here it is:\n\n**To:** sarah.johnson@techstart.com\n**Subject:** Following up on our conversation\n\nHi Sarah,\n\nThank you for taking the time to meet with me yesterday. I appreciated the opportunity to discuss how our services could benefit TechStart.\n\nAs promised, I will send over the detailed proposal by Friday for your review.\n\nI'm looking forward to our follow-up call next Tuesday at 2pm to address any questions you might have and discuss potential next steps.\n\nPlease let me know if you need any additional information in the meantime.\n\nBest regards,\n[Your Name]\n\nWould you like to make any changes to this email before sending it?",
        ]
    ),
)


# Add the goals to the goal_list
goal_list = [
    goal_choose_agent_type,
    goal_find_leads,
    goal_enrich_leads,
    goal_generate_emails,
    goal_draft_email
]


# for multi-goal, just set list agents as the last tool
first_goal_value = os.getenv("AGENT_GOAL")
if first_goal_value is None:
    multi_goal_mode = True  # default if unset
elif (
    first_goal_value is not None
    and first_goal_value.lower() != "goal_choose_agent_type"
):
    multi_goal_mode = False
else:
    multi_goal_mode = True

if multi_goal_mode:
    for goal in goal_list:
        list_agents_found: bool = False
        for tool in goal.tools:
            if tool.name == "ListAgents":
                list_agents_found = True
                continue
        if list_agents_found == False:
            goal.tools.append(tool_registry.list_agents_tool)
            continue
