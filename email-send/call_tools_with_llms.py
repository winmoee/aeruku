from openai import OpenAI

client = OpenAI(
    base_url="https://api.arcade.dev/v1",
    api_key="arc_o16XZfJoJxU69gYxXfMbofuRB8EUceeQue3SeDiCmbzY8A69EaEY",
)

user_id = "aeruku1@gmail.com"

tools = [
    "GitHub.SetStarred",
    "Google.WriteDraftEmail@1.2.1",
    "Google.SendEmail@1.2.1",
    "Google.SendDraftEmail@1.2.1",
]

def draft_email(args: dict) -> dict:
    prompt = args.get("prompt", "Draft a professional email")

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that can create draft emails and send them on Gmail."},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o",
        user=user_id,
        tools=tools,
        tool_choice="generate",
    )

    return {
        "response": response.choices[0].message.content
    }

args = {"prompt": "Johns email is john@gmail.com and the meeting is on Tuesday focused on Chicken"}
result = draft_email(args)
print(result["response"])