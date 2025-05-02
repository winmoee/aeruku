from arcadepy import Arcade

client = Arcade()

user_id = "aeruku1@gmail.com"


auth_response = client.tools.authorize(
    tool_name="Google.WriteDraftEmail",
    user_id=user_id,
)


def draft_email(args: dict) -> dict:        
    client.auth.wait_for_completion(auth_response)

    tool_input = {
        "recipient": args["recipient_email"],
        "subject": args["subject"],
        "body": args["body"],
    }

    print(tool_input)

    response = client.tools.execute(
        tool_name="Google.WriteDraftEmail",
        input=tool_input,
        user_id=user_id,
    )

    print(response)

    return {
        "response": response
    }


