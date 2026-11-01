import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_match_notification(case_id: str, case_details: tuple) -> bool:
    """
    Send an email notification using the Brevo Transactional Email API.
    """

    brevo_api_key = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("BREVO_SENDER_EMAIL")
    sender_name = os.environ.get("BREVO_SENDER_NAME", "Missing Person Identification System")

    if not brevo_api_key or not sender_email:
        print("[emailer] Brevo environment variables are not fully configured.")
        return False

    # case_details:
    # (name, complainant_mobile, complainant_email, age, last_seen, birth_marks)

    name = case_details[0] if case_details else "Unknown"
    complainant_email = case_details[2] if len(case_details) > 2 else None
    age = case_details[3] if len(case_details) > 3 else "N/A"
    last_seen = case_details[4] if len(case_details) > 4 else "N/A"

    recipient = complainant_email or os.environ.get("NOTIFY_EMAIL")

    if not recipient:
        print("[emailer] No recipient email available.")
        return False

    subject = f"Match Found - {name}"

    body = f"""
Hello,

A match has been found for the following missing person case.

Case Details:

Name: {name}
Age: {age}
Last Seen: {last_seen}
Case ID: {case_id}

Please log in to the Missing Person Identification System to review and confirm the match.

This is an automated notification. Please do not reply to this email.
"""

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient,
            }
        ],
        "subject": subject,
        "textContent": body,
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=15,
        )

        if response.status_code in (200, 201, 202):
            print(
                f"[emailer] Brevo notification sent to {recipient} "
                f"for case {case_id}"
            )
            return True

        print(
            f"[emailer] Brevo API error: "
            f"{response.status_code} - {response.text}"
        )
        return False

    except Exception as exc:
        print(f"[emailer] Failed to send Brevo email: {exc}")
        return False