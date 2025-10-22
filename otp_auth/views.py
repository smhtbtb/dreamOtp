from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from otp_auth.services.otp_service import generate_otp, verify_otp
from otp_auth.serializers import RequestOTPSerializer, VerifyOTPSerializer


class RequestOTPView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data["identifier"]
            state, res = generate_otp(identifier)
            return Response({"message": "OTP sent"}, status=status.HTTP_200_OK) if state else Response(
                {"message": f"Previous OTP is still valid. Time to expiration is {res} seconds"},
                status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data["identifier"]
            code = serializer.validated_data["code"]

            user = verify_otp(identifier, code)
            if user:
                login(request, user)
                return Response(
                    {
                        "message": "Login successful",
                        "user": user.username,
                        "email": user.email,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": "Invalid or expired OTP. Please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
