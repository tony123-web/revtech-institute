import os
import requests

from django.template.loader import render_to_string
from dotenv import load_dotenv

load_dotenv()


def send_brevo_email(
    *,
    recipient_email,
    recipient_name="",
    subject,
    template=None,
    context=None,
    text_content="",
    html_content=None,
):
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("DEFAULT_FROM_EMAIL")

    if not api_key:
        print("BREVO_API_KEY is missing.")
        return False

    if not sender_email:
        print("DEFAULT_FROM_EMAIL is missing.")
        return False

    if not recipient_email:
        print("Recipient email is missing.")
        return False

    if html_content is None and template:
        html_content = render_to_string(
            template,
            context or {}
        )

    payload = {
        "sender": {
            "email": sender_email,
            "name": "RevTech Institute",
        },
        "to": [
            {
                "email": recipient_email,
                "name": recipient_name,
            }
        ],
        "subject": subject,
        "htmlContent": html_content or "",
    }

    if text_content:
        payload["textContent"] = text_content

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json=payload,
            timeout=30,
        )

        if response.status_code == 201:
            return True

        print(
            "BREVO ERROR:",
            response.status_code,
            response.text,
        )

    except requests.RequestException as error:
        print(
            "BREVO CONNECTION ERROR:",
            error,
        )

    return False


def send_payment_confirmation_email(enrollment):
    student = enrollment.student

    return send_brevo_email(
        recipient_email=student.email,
        recipient_name=(
            student.get_full_name()
            or student.username
        ),
        subject="Payment Confirmed — RevTech Institute",
        template="accounts/emails/payment_confirmation_email.html",
        context={
            "student": student,
            "enrollment": enrollment,
            "cohort": enrollment.cohort,
        },
        text_content=(
            f"Hello {student.first_name},\n\n"
            "Your payment has been successfully confirmed.\n\n"
            f"Cohort: {enrollment.cohort.name}\n"
            f"Amount paid: ₦{enrollment.amount_paid:,.2f}\n\n"
            "Your enrollment is now active.\n\n"
            "Welcome to RevTech Institute!\n\n"
            "Regards,\n"
            "RevTech Institute"
        ),
    )











