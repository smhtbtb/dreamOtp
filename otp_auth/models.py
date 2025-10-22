from django.conf import settings
from django.db import models
from django.utils import timezone

from otp_auth.constants.enums import IdentifierType


class OTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
        null=True,
        blank=True,
    )
    identifier_type = models.CharField(
        max_length=10, choices=IdentifierType.choices()
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return (
                not self.is_used
                and (timezone.now() - self.created_at).total_seconds() < settings.OTP_EXPIRATION_MINUTES * 60
        )

    def __str__(self):
        user_name = self.user.username if self.user else "-"
        return f"OTP({self.code}) for {user_name} [{self.identifier_type}]"
