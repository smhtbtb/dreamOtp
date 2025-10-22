from django.conf import settings


def send_sms(phone_number, code):
    print(f"[Fake SMS API] Sending OTP {code} to {phone_number} by {settings.FAKE_SMS_API_URL} API")
