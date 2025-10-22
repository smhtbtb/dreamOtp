from rest_framework import serializers
from otp_auth.constants.enums import IdentifierType


class RequestOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)

    def validate_identifier(self, value):
        if "@" in value:
            self.identifier_type = IdentifierType.EMAIL
        elif value.isdigit():
            self.identifier_type = IdentifierType.PHONE
        else:
            raise serializers.ValidationError("Invalid identifier (must be email or phone).")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=6)

    def validate_identifier(self, value):
        if "@" in value:
            self.identifier_type = IdentifierType.EMAIL
        elif value.isdigit():
            self.identifier_type = IdentifierType.PHONE
        else:
            raise serializers.ValidationError("Invalid identifier (must be email or phone).")
        return value
