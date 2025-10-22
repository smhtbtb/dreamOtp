from django.contrib.auth import get_user_model
from django.db import transaction
from otp_auth.constants.enums import IdentifierType

User = get_user_model()

@transaction.atomic
def get_or_create_user(identifier: str, identifier_type: IdentifierType):
    if identifier_type == IdentifierType.EMAIL:
        user, _ = User.objects.get_or_create(
            email=identifier,
            defaults={"username": identifier.split("@")[0]},
        )
    elif identifier_type == IdentifierType.PHONE:
        user, _ = User.objects.get_or_create(
            username=identifier,
            defaults={"email": ""},
        )
    else:
        raise ValueError("Unsupported identifier type")

    return user
