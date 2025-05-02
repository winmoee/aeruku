from typing import Dict, Optional, TypedDict
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class FollowUp(TypedDict):
    daysAfter: int
    subject: str
    body: str

class EmailDraft(TypedDict):
    subject: str
    body: str
    followUp: Optional[FollowUp]

def generate_email(args: dict) -> dict:
    """
    Generate a personalized email based on lead information and preferences using OpenAI.
    
    Args:
        args: Dictionary containing:
            - lead_name: Name of the lead contact person
            - company_name: Name of the company
            - title: Job title of the lead contact person
            - product_description: Description of the product/service
            
    Returns:
        dict: Email draft containing subject, body and follow-up email
    """
    lead_name = args.get('lead_name', 'there')
    company_name = args.get('company_name', 'your company')
    title = args.get('title', '')
    product_description = args.get('product_description', '')

    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Generate main email using OpenAI
    prompt = f"""Generate a professional business email with the following details:
    - Recipient: {lead_name}
    - Company: {company_name}
    - Title: {title}
    - Product: {product_description}
    
    The email should be concise, professional, and focused on starting a conversation about the product.
    Include a subject line and body."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional business email writer."},
            {"role": "user", "content": prompt}
        ]
    )

    # Parse the response to get subject and body
    email_content = response.choices[0].message.content
    subject = email_content.split('\n')[0].replace('Subject: ', '')
    body = '\n'.join(email_content.split('\n')[1:])

    # Generate follow-up email
    followup_prompt = f"""Generate a professional follow-up email with the following details:
    - Recipient: {lead_name}
    - Company: {company_name}
    - Product: {product_description}
    
    The email should be a gentle follow-up to the initial outreach."""

    followup_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional business email writer."},
            {"role": "user", "content": followup_prompt}
        ]
    )

    followup_content = followup_response.choices[0].message.content
    followup_subject = followup_content.split('\n')[0].replace('Subject: ', '')
    followup_body = '\n'.join(followup_content.split('\n')[1:])

    followup: FollowUp = {
        "daysAfter": 3,
        "subject": followup_subject,
        "body": followup_body
    }

    email_draft: EmailDraft = {
        "subject": subject,
        "body": body,
        "followUp": followup
    }

    # Format the response for better readability
    formatted_response = f"""
Generated Email:

Subject: {subject}

{body}

Follow-up Email (to be sent after 3 days):

Subject: {followup_subject}

{followup_body}
"""

    # Store the email draft in a format that can be accessed by the draft email functionality
    stored_email = {
        "email_draft": email_draft,
        "formatted_response": formatted_response,
        "metadata": {
            "lead_name": lead_name,
            "company_name": company_name,
            "title": title,
            "product_description": product_description
        }
    }

    return {
        "response": formatted_response,
        "email_draft": email_draft,
        "stored_email": stored_email
    }