from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from otp_auth.models import OTP

User = get_user_model()


class OTPAuthTests(APITestCase):
    def setUp(self):
        self.email = "user@example.com"
        self.phone = "09120001122"
        self.request_url = reverse("request_otp")
        self.verify_url = reverse("verify_otp")

    def test_request_otp_creates_record_for_email(self):
        response = self.client.post(self.request_url, {"identifier": self.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        otp = OTP.objects.last()
        self.assertIsNotNone(otp)
        self.assertEqual(otp.user.email, self.email)
        self.assertFalse(otp.is_used)

    def test_request_otp_creates_record_for_phone(self):
        response = self.client.post(self.request_url, {"identifier": self.phone})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        otp = OTP.objects.last()
        self.assertIsNotNone(otp)
        self.assertEqual(otp.user.username, self.phone)

    def test_verify_otp_success(self):
        self.client.post(self.request_url, {"identifier": self.email})
        otp = OTP.objects.last()
        res = self.client.post(self.verify_url, {"identifier": self.email, "code": otp.code})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)

    def test_verify_otp_invalid_code(self):
        self.client.post(self.request_url, {"identifier": self.email})
        res = self.client.post(self.verify_url, {"identifier": self.email, "code": "999999"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_request_new_otp_if_active_exists(self):
        # First OTP
        self.client.post(self.request_url, {"identifier": self.email})
        res = self.client.post(self.request_url, {"identifier": self.email})
        # should return 429 Too Many Requests
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("remaining_seconds", res.json())
