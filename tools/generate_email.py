from typing import Dict, Optional, TypedDict

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
    Generate a personalized email based on lead information and preferences.
    
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

    # Generate main email
    subject = f"Discussing {product_description.split()[0]} solutions for {company_name}"
    
    body = f"""Hi {lead_name},

I hope this message finds you well. I noticed your role as {title} at {company_name} and wanted to reach out regarding {product_description}.

I believe our solution could be particularly valuable for your team. Would you be open to a brief conversation to discuss how we might help?

Best regards,
[Your Name]"""

    # Generate follow-up email
    followup: FollowUp = {
        "daysAfter": 3,
        "subject": f"Following up: {subject}",
        "body": f"""Hi {lead_name},

I wanted to follow up on my previous email about {product_description}. I'd love to hear your thoughts on how we could potentially help {company_name}.

Would you be available for a quick chat this week?

Best regards,
[Your Name]"""
    }

    email_draft: EmailDraft = {
        "subject": subject,
        "body": body,
        "followUp": followup
    }

    return email_draft