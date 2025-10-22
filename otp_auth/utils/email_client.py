from django.core.mail import send_mail as django_send_mail
from django.conf import settings
import logging

def send_email(to_email: str, code: str):
    subject = "Your One-Time Password (OTP)"
    message = f"Your login code is: {code}\n\nThis code will expire in {settings.OTP_EXPIRATION_MINUTES} minutes."
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        django_send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        print(f"OTP email sent to {to_email}")
    except:
        print(f"[FAKE EMAIL] Sent OTP {code} to {to_email}")
