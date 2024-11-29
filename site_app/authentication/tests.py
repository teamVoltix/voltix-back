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
            "dni": "1234567A",
            "email": "test@example.com",
            "password": "Test1234!"
        }
        self.user = User.objects.create(
            fullname=self.user_data["fullname"],
            dni=self.user_data["dni"],
            email=self.user_data["email"],
            password=make_password(self.user_data["password"]),
        )
        # Crear un perfil asociado si existe la relación
        self.profile = self.user.profile if hasattr(self.user, 'profile') else None


    ##############################
    # Tests for User Registration
    ##############################

    def test_registration_with_valid_dni(self):
        """Test registration with a valid DNI."""
        response = self.client.post(reverse('register'), data={
            "fullname": "John Doe",
            "dni": "12345678A",  # Válido: máximo 9 caracteres y al menos una letra
            "email": "johndoe@example.com",
            "password": "Password123!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)




    def test_registration_with_invalid_dni_length(self):
        """Test registration fails if DNI has more than 9 characters."""
        response = self.client.post(reverse('register'), data={
            "fullname": "John Doe",
            "dni": "1234567890",  # Más de 9 caracteres
            "email": "johndoe@example.com",
            "password": "Password123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("El DNI no puede tener más de 9 caracteres.", str(response.data))







    def test_registration_with_dni_without_letters(self):
        """Test registration fails if DNI does not contain the correct number of letters."""
        response = self.client.post(reverse('register'), data={
            "fullname": "John Doe",
            "dni": "123456789",  # No contiene ninguna letra
            "email": "johndoe@example.com",
            "password": "Password123!"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "El DNI que comienza con un número debe tener 8 números seguidos de 1 letra (ejemplo: 12345678A).",
            str(response.data)
        )




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
        uid = urlsafe_base64_encode(smart_bytes(self.user.pk))
        token = "expiredtoken123"
        response = self.client.post(reverse('password_reset', args=[uid, token]), data={
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    ##############################
    # Tests for Logout
    ##############################

    def test_logout_with_invalid_token(self):
        """Test logout fails with invalid refresh token."""
        response = self.client.post(reverse('logout'), data={
            "refresh_token": "invalid_refresh_token"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_authentication(self):
        """Test logout fails without authentication."""
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    ##############################
    # Borrar los users creados
    ##############################

    def tearDown(self):
        # Eliminar el perfil si existe
        if self.profile:
            self.profile.delete()
        # Eliminar el usuario
        self.user.delete()
