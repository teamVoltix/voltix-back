from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.hashers import make_password
from voltix.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


class AuthenticationTests(TestCase):
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

    def test_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(reverse('user-registration'), data={
            "fullname": "New User",
            "dni": "987654321",
            "email": "newuser@example.com",
            "password": "NewPass123!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Usuario registrado exitosamente")

    def test_registration_missing_fields(self):
        """Test registration fails when required fields are missing."""
        response = self.client.post(reverse('user-registration'), data={
            "fullname": "New User"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_duplicate_email(self):
        """Test registration fails with duplicate email."""
        response = self.client.post(reverse('user-registration'), data={
            "fullname": "Another User",
            "dni": "987654321",
            "email": self.user_data["email"],
            "password": "AnotherPass123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_invalid_email_format(self):
        """Test registration fails with invalid email format."""
        response = self.client.post(reverse('user-registration'), data={
            "fullname": "New User",
            "dni": "987654321",
            "email": "invalid-email",
            "password": "ValidPass123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_weak_password(self):
        """Test registration fails with weak password."""
        weak_passwords = ["short", "alllowercase1", "ALLUPPERCASE1", "NoNumber!", "12345678"]
        for password in weak_passwords:
            response = self.client.post(reverse('user-registration'), data={
                "fullname": "New User",
                "dni": "987654321",
                "email": "newuser@example.com",
                "password": password
            })
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_success_edge_case(self):
        """Test registration with edge case values (max length, special chars)."""
        response = self.client.post(reverse('user-registration'), data={
            "fullname": "Test " * 50,
            "dni": "1234567890",
            "email": "valid_email@example.com",
            "password": "StrongPass123!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    ##############################
    # Tests for User Login
    ##############################

    def test_login_success(self):
        """Test successful user login."""
        response = self.client.post(reverse('login'), data={
            "dni": self.user_data["dni"],
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

    def test_login_invalid_password(self):
        """Test login fails with invalid password."""
        response = self.client.post(reverse('login'), data={
            "dni": self.user_data["dni"],
            "password": "WrongPassword123"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalid_dni(self):
        """Test login fails with invalid DNI."""
        response = self.client.post(reverse('login'), data={
            "dni": "000000000",
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Test login fails when fields are missing."""
        response = self.client.post(reverse('login'), data={
            "dni": self.user_data["dni"]
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ##############################
    # Tests for Protected Views
    ##############################

    def test_protected_view_with_valid_token(self):
        """Test access to a protected view with a valid token."""
        response = self.client.post(reverse('login'), data={
            "dni": self.user_data["dni"],
            "password": self.user_data["password"]
        })
        access_token = response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(reverse('protected-view'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_view_with_invalid_token(self):
        """Test access to a protected view with an invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = self.client.get(reverse('protected-view'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    ##############################
    # Tests for Logout
    ##############################

    def test_logout_success(self):
        """Test user logout successfully blacklists the refresh token."""
        login_response = self.client.post(reverse('login'), data={
            "dni": self.user_data["dni"],
            "password": self.user_data["password"]
        })
        refresh_token = login_response.data["refresh_token"]
        response = self.client.post(reverse('logout'), data={"refresh_token": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_invalid_refresh_token(self):
        """Test logout fails with invalid refresh token."""
        response = self.client.post(reverse('logout'), data={"refresh_token": "invalid-token"})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    ##############################
    # Tests for Password Reset
    ##############################

    def test_password_reset_request_success(self):
        """Test password reset request for valid email."""
        response = self.client.post(reverse('password-reset-request'), data={
            "email": self.user_data["email"]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email."""
        response = self.client.post(reverse('password-reset-request'), data={
            "email": "nonexistent@example.com"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_success(self):
        """Test password reset successfully updates the password."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.post(reverse('password-reset', args=[uid, token]), data={
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_invalid_token(self):
        """Test password reset fails with an invalid token."""
        uid = "invalid_uid"
        token = "invalid_token"
        response = self.client.post(reverse('password-reset', args=[uid, token]), data={
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ##############################
    # Tests for Change Password
    ##############################

    def test_change_password_success(self):
        """Test successfully changing the password."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('change-password'), data={
            "old_password": self.user_data["password"],
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_invalid_old_password(self):
        """Test changing the password fails with incorrect old password."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('change-password'), data={
            "old_password": "WrongPassword123",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
