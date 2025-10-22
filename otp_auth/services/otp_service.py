import random

from django.conf import settings
from django.utils import timezone

from otp_auth.constants.enums import IdentifierType
from otp_auth.models import OTP
from otp_auth.services.define_user import get_or_create_user
from otp_auth.utils.email_client import send_email
from otp_auth.utils.sms_client import send_sms


def _detect_identifier_type(identifier: str) -> IdentifierType:
    return IdentifierType.EMAIL if "@" in identifier else IdentifierType.PHONE


def generate_otp(identifier):
    identifier_type = _detect_identifier_type(identifier)
    user = get_or_create_user(identifier, identifier_type)

    active_otp = OTP.objects.filter(
        user=user, is_used=False
    ).order_by("-created_at").first()

    if active_otp:
        elapsed = (timezone.now() - active_otp.created_at).total_seconds()
        if elapsed < settings.OTP_EXPIRATION_MINUTES * 60:
            remaining = int(settings.OTP_EXPIRATION_MINUTES * 60 - elapsed)
            return False, remaining
    OTP.objects.filter(user=user, is_used=False).update(is_used=True)

    # create new otp
    code = str(random.randint(100000, 999999))
    otp = OTP.objects.create(
        user=user,
        identifier_type=identifier_type.value,
        code=code
    )

    if identifier_type is IdentifierType.PHONE:
        send_sms(user.username, f"Your login code is {code}")
    else:
        send_email(user.email, code)

    return True, otp


def verify_otp(identifier: str, code: str):
    identifier_type = IdentifierType.EMAIL if "@" in identifier else IdentifierType.PHONE
    user = get_or_create_user(identifier, identifier_type)

    otp = (
        OTP.objects.filter(user=user, code=code, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if otp and otp.is_valid():
        otp.is_used = True
        otp.save()
        return user

    return None
