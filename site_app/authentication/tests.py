from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.hashers import make_password
from voltix.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes, force_str


class ExtendedAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "fullname": "Test User",
            "dni": "123456789",
            "email": "test@example.com",
            "password": "Test1234!"
        }
        self.user = User.objects.create(
            fullname=self.user_data["fullname"],
            dni=self.user_data["dni"],
            email=self.user_data["email"],
            password=make_password(self.user_data["password"]),
        )

    ##############################
    # Tests for User Registration
    ##############################

    def test_registration_with_special_characters_in_name(self):
        """Test registration with names containing special characters."""
        response = self.client.post(reverse('register'), data={
            "fullname": "Ñandú Pérez",
            "dni": "987654321",
            "email": "specialchar@example.com",
            "password": "ValidPass123!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_with_long_dni(self):
        """Test registration with a very long DNI."""
        response = self.client.post(reverse('register'), data={
            "fullname": "Long DNI",
            "dni": "12345678901234567890",
            "email": "longdni@example.com",
            "password": "ValidPass123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_malformed_json(self):
        """Test registration with invalid JSON format."""
        response = self.client.post(
            reverse('register'),
            data="{'malformed': 'json'}",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ##############################
    # Tests for User Login
    ##############################

    def test_login_with_inactive_user(self):
        """Test login with an inactive user."""
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse('login'), data={
            "dni": self.user_data["dni"],
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_spaces_in_dni(self):
        """Test login with spaces in DNI."""
        response = self.client.post(reverse('login'), data={
            "dni": " 123456789 ",
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    ##############################
    # Tests for Change Password
    ##############################

    def test_change_password_matching_old_password(self):
        """Test change password fails when the new password matches the old one."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('change_password'), data={
            "old_password": self.user_data["password"],
            "new_password": self.user_data["password"],
            "confirm_new_password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_without_confirmation(self):
        """Test change password fails when confirmation is missing."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('change_password'), data={
            "old_password": self.user_data["password"],
            "new_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ##############################
    # Tests for Password Reset
    ##############################

    def test_password_reset_with_expired_token(self):
        """Test password reset fails with an expired token."""
        uid = urlsafe_base64_encode(smart_bytes(self.user.pk))  # Updated here
        token = "expiredtoken123"
        response = self.client.post(reverse('password_reset', args=[uid, token]), data={
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ##############################
    # Tests for Logout
    ##############################

    def test_logout_with_invalid_token(self):
        """Test logout fails with invalid refresh token."""
        response = self.client.post(reverse('logout'), data={
            "refresh_token": "invalid_refresh_token"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_without_authentication(self):
        """Test logout fails without authentication."""
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
