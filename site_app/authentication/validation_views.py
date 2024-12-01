# este archivo contiene funcionalidad para endpoint validacion y validate
# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from voltix.models import EmailVerification, User
import random
import string
from rest_framework.permissions import AllowAny
# from django.contrib.auth import get_user_model
# User = get_user_model()

#1
class RequestVerificationCodeView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si usuario con este correo está registrado
        if User.objects.filter(email=email).exists():
            return Response({"error": "This email is already registered."}, status=status.HTTP_404_NOT_FOUND)
        
        # Count expired codes in the last hour
        one_hour_ago = now() - timedelta(hours=1)
        expired_codes_count = EmailVerification.objects.filter(
            email=email,
            is_used=False,
            code_expiration__lt=now(),
            created_at__gte=one_hour_ago,
        ).count()

        # Limit to 3 expired codes per hour
        if expired_codes_count >= 3:
            return Response(
                {"error": "Too many attempts. Please try again in an hour."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )


        # Generate a 6-digit numerical code
        code = f"{random.randint(100000, 999999)}"

        # Set the default expiration time
        expiration_time = now() + timedelta(minutes=10)

        # Create or update the verification record
        verification, created = EmailVerification.objects.get_or_create(
            email=email,
            defaults={
                'code_expiration': expiration_time,
                'is_used': False,
            }
        )

        if not created and not verification.is_code_expired():
            return Response({"message": "A code has already been sent. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Update the code and expiration for existing records
        verification.set_verification_code(code)
        verification.code_expiration = expiration_time
        verification.is_used = False
        verification.save()

        # # Send the code via email
        # send_mail(
        #     'Your Verification Code',
        #     f'Your verification code is {code}. It expires in 10 minutes.',
        #     'no-reply@example.com',
        #     [email],
        #     fail_silently=False,
        # )

        # return Response({"message": "Verification code sent."}, status=status.HTTP_200_OK)

        return Response({"message": "Verification code generated and logged."}, status=status.HTTP_200_OK)




#2

class ValidateVerificationCodeView(APIView):

    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "Email and code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification = EmailVerification.objects.get(email=email, is_used=False)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Invalid email or code."}, status=status.HTTP_404_NOT_FOUND)

        # Check if code is expired
        if verification.is_code_expired():
            return Response({"error": "The code has expired. Please request a new one."}, status=status.HTTP_410_GONE)

        # Check if the code matches
        if not verification.check_verification_code(code):
            verification.attempts += 1
            verification.save()

            if verification.attempts > 2:
                return Response({"error": "Too many failed attempts. Please request a new code."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            return Response({"error": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark verification as successful
        verification.is_used = True
        verification.save()

        return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)

#3
#serializer de registration
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError




class RegistrationSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password', 'fullname', 'dni']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if not EmailVerification.objects.filter(email=value, is_used=True).exists():
            raise ValidationError("Email has not been verified.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class RegistrationView(APIView):

    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Clean up verification record
            EmailVerification.objects.filter(email=serializer.validated_data['email']).delete()

            return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
