import pytest
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from otp_auth.models import OTP
from otp_auth.services import otp_service
from otp_auth.constants.enums import IdentifierType


@pytest.mark.django_db
class TestOTPServiceLogic:
    """Unit tests for otp_auth.services.otp_service"""

    # --- Identifier detection -------------------------------------------------

    def test_detect_identifier_type_email_and_phone(self):
        assert otp_service._detect_identifier_type("user@example.com") == IdentifierType.EMAIL
        assert otp_service._detect_identifier_type("09120001122") == IdentifierType.PHONE

    # --- OTP generation -------------------------------------------------------

    def test_generate_otp_creates_new_email_otp(self, monkeypatch):
        """Should create an OTP and send an email."""
        called = {}

        monkeypatch.setattr(
            "otp_auth.services.otp_service.send_email",
            lambda email, code: called.update({"email": email, "code": code}),
        )

        ok, otp = otp_service.generate_otp("user@example.com")

        assert ok is True
        assert isinstance(otp, OTP)
        assert otp.identifier_type == IdentifierType.EMAIL.value
        assert called["email"] == "user@example.com"
        assert len(otp.code) == 6

    def test_generate_otp_creates_new_phone_otp(self, monkeypatch):
        """Should create an OTP and send an SMS."""
        called = {}

        monkeypatch.setattr(
            "otp_auth.services.otp_service.send_sms",
            lambda phone, text: called.update({"phone": phone, "text": text}),
        )

        ok, otp = otp_service.generate_otp("09120001122")

        assert ok is True
        assert otp.identifier_type == IdentifierType.PHONE.value
        assert called["phone"] == "09120001122"
        assert "Your login code" in called["text"]

    def test_generate_otp_blocks_if_active_exists(self):
        """If a valid OTP exists, should not create a new one."""
        identifier = "foo@example.com"

        ok, otp = otp_service.generate_otp(identifier)
        assert ok is True

        ok2, remaining = otp_service.generate_otp(identifier)
        assert ok2 is False
        assert isinstance(remaining, int)
        assert 0 < remaining <= settings.OTP_EXPIRATION_MINUTES * 60

    def test_generate_otp_allows_new_after_expiration(self):
        """After the OTP expires, a new one should be generated."""
        identifier = "user2@example.com"
        ok, otp = otp_service.generate_otp(identifier)
        assert ok

        otp.created_at = timezone.now() - timedelta(minutes=settings.OTP_EXPIRATION_MINUTES + 1)
        otp.save()

        ok2, otp2 = otp_service.generate_otp(identifier)
        assert ok2 is True
        assert otp2 != otp

    # --- OTP verification -----------------------------------------------------

    def test_verify_otp_valid_marks_used(self):
        """Valid OTP should return user and mark it used."""
        identifier = "bar@example.com"
        ok, otp = otp_service.generate_otp(identifier)

        user = otp_service.verify_otp(identifier, otp.code)

        assert user == otp.user
        otp.refresh_from_db()
        assert otp.is_used is True

    def test_verify_otp_invalid_code_returns_none(self):
        """Invalid OTP code should return None."""
        identifier = "baz@example.com"
        otp_service.generate_otp(identifier)
        result = otp_service.verify_otp(identifier, "000000")
        assert result is None

    def test_verify_otp_expired_returns_none(self):
        """Expired OTP should not verify."""
        identifier = "old@example.com"
        ok, otp = otp_service.generate_otp(identifier)

        otp.created_at = timezone.now() - timedelta(minutes=settings.OTP_EXPIRATION_MINUTES + 1)
        otp.save()

        result = otp_service.verify_otp(identifier, otp.code)
        assert result is None

    def test_verify_otp_cannot_be_reused(self):
        """Once OTP is used, it cannot be verified again."""
        identifier = "reuse@example.com"
        ok, otp = otp_service.generate_otp(identifier)

        user = otp_service.verify_otp(identifier, otp.code)
        assert user

        again = otp_service.verify_otp(identifier, otp.code)
        assert again is None
