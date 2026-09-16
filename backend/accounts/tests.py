from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import override_settings
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserRole


class UserRoleTests(TestCase):
    def test_user_defaults_to_student_role(self):
        user = User(username="default-user")

        self.assertEqual(user.role, UserRole.STUDENT)
        self.assertTrue(user.is_student)

    def test_supported_roles_are_accepted(self):
        roles = (
            (UserRole.STUDENT, "is_student"),
            (UserRole.PARENT, "is_parent"),
            (UserRole.TUTOR, "is_tutor"),
            (UserRole.ADMIN, "is_admin_role"),
        )

        for role, helper_name in roles:
            with self.subTest(role=role):
                user = User(
                    username=f"{role}-user",
                    email=f"{role}@example.com",
                    role=role,
                )
                user.set_unusable_password()
                user.full_clean()
                self.assertTrue(getattr(user, helper_name))

    def test_invalid_role_fails_model_validation(self):
        user = User(username="invalid-role-user", role="invalid")

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_application_admin_role_does_not_grant_django_admin_privileges(self):
        user = User(username="application-admin", role=UserRole.ADMIN)

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_role_representation_does_not_expose_password(self):
        user = User(username="safe-user", role=UserRole.TUTOR)
        user.set_password("a-secret-password")

        representation = str(user)

        self.assertEqual(representation, "safe-user")
        self.assertNotIn("a-secret-password", representation)
        self.assertNotIn(user.password, representation)


class RegistrationApiTests(APITestCase):
    registration_url = "/api/auth/register/"
    password = "StrongPassword123!"

    def registration_data(self, **overrides):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "password": self.password,
            "password_confirm": self.password,
            "role": UserRole.STUDENT,
        }
        data.update(overrides)
        return data

    def test_valid_student_registration(self):
        response = self.client.post(self.registration_url, self.registration_data())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], UserRole.STUDENT)
        self.assertEqual(response.data["email"], "jane@example.com")
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_hash", response.data)

    def test_valid_parent_and_tutor_registration(self):
        for role, email in (
            (UserRole.PARENT, "parent@example.com"),
            (UserRole.TUTOR, "tutor@example.com"),
        ):
            with self.subTest(role=role):
                response = self.client.post(
                    self.registration_url,
                    self.registration_data(role=role, email=email),
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_email_is_rejected(self):
        self.client.post(self.registration_url, self.registration_data())

        response = self.client.post(
            self.registration_url,
            self.registration_data(first_name="Different"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_is_normalized(self):
        response = self.client.post(
            self.registration_url,
            self.registration_data(email="  Jane@EXAMPLE.COM "),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "jane@example.com")

    def test_invalid_email_is_rejected(self):
        response = self.client.post(
            self.registration_url,
            self.registration_data(email="not-an-email"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch_is_rejected(self):
        response = self.client.post(
            self.registration_url,
            self.registration_data(password_confirm="DifferentPassword123!"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            self.registration_url,
            self.registration_data(password="password", password_confirm="password"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_required_fields_are_validated(self):
        response = self.client.post(self.registration_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("first_name", "last_name", "email", "password", "password_confirm", "role"):
            self.assertIn(field, response.data)

    def test_admin_role_is_rejected(self):
        response = self.client.post(
            self.registration_url,
            self.registration_data(role=UserRole.ADMIN),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_hashed_and_privilege_fields_are_not_submitted(self):
        response = self.client.post(self.registration_url, self.registration_data())
        user = get_user_model().objects.get(email="jane@example.com")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(user.password, self.password)
        self.assertNotIn(self.password, user.password)
        self.assertTrue(user.password.startswith("pbkdf2_"))
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_privilege_fields_cannot_be_submitted(self):
        for field in ("is_staff", "is_superuser", "groups", "user_permissions"):
            with self.subTest(field=field):
                response = self.client.post(
                    self.registration_url,
                    self.registration_data(**{field: True}),
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginApiTests(APITestCase):
    login_url = "/api/auth/login/"
    password = "StrongPassword123!"

    def setUp(self):
        self.user = User.objects.create_user(
            username="login@example.com",
            email="login@example.com",
            password=self.password,
            first_name="Login",
            last_name="User",
            role=UserRole.STUDENT,
        )

    def test_valid_credentials_return_safe_user_information(self):
        response = self.client.post(
            self.login_url,
            {"email": "login@example.com", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "login@example.com")
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_hash", response.data)
        self.assertNotIn("is_staff", response.data)
        self.assertNotIn("is_superuser", response.data)

    def test_correct_password_authenticates_successfully(self):
        response = self.client.post(
            self.login_url,
            {"email": "login@example.com", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_password_has_safe_generic_error(self):
        response = self.client.post(
            self.login_url,
            {"email": "login@example.com", "password": "WrongPassword123!"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Invalid email or password."})

    def test_email_is_normalized(self):
        response = self.client.post(
            self.login_url,
            {"email": "  LOGIN@EXAMPLE.COM ", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_password_and_unknown_email_use_generic_error(self):
        invalid_password = self.client.post(
            self.login_url,
            {"email": "login@example.com", "password": "WrongPassword123!"},
        )
        unknown_email = self.client.post(
            self.login_url,
            {"email": "unknown@example.com", "password": self.password},
        )

        self.assertEqual(invalid_password.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(unknown_email.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_password.data, {"detail": "Invalid email or password."})
        self.assertEqual(unknown_email.data, {"detail": "Invalid email or password."})

    def test_inactive_account_is_rejected_with_generic_error(self):
        self.user.is_active = False
        self.user.save(update_fields=("is_active",))

        response = self.client.post(
            self.login_url,
            {"email": "login@example.com", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Invalid email or password."})

    def test_missing_and_malformed_input_is_rejected(self):
        missing_fields = self.client.post(self.login_url, {})
        malformed_email = self.client.post(
            self.login_url,
            {"email": "not-an-email", "password": self.password},
        )
        missing_password = self.client.post(
            self.login_url,
            {"email": "login@example.com"},
        )

        self.assertEqual(missing_fields.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(malformed_email.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(missing_password.status_code, status.HTTP_400_BAD_REQUEST)


class TokenAndProtectedApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="token@example.com",
            email="token@example.com",
            password="StrongPassword123!",
            role=UserRole.TUTOR,
        )

    def test_token_obtain_and_refresh(self):
        response = self.client.post(
            "/api/auth/token/",
            {"email": "token@example.com", "password": "StrongPassword123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refresh = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": response.data["refresh"]},
        )
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh.data)

    def test_token_invalid_credentials_have_safe_generic_error(self):
        response = self.client.post(
            "/api/auth/token/",
            {"email": "unknown@example.com", "password": "WrongPassword123!"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("active account", str(response.data).lower())
        self.assertIn("Invalid email or password.", str(response.data))

    def test_token_inactive_account_has_safe_generic_error(self):
        self.user.is_active = False
        self.user.save(update_fields=("is_active",))

        response = self.client.post(
            "/api/auth/token/",
            {"email": "token@example.com", "password": "StrongPassword123!"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("active account", str(response.data).lower())
        self.assertIn("Invalid email or password.", str(response.data))

    def test_current_user_requires_and_returns_authenticated_user(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "token@example.com")
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_hash", response.data)

    def test_logout_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": str(refresh)},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        refreshed = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": str(refresh)},
        )
        self.assertEqual(refreshed.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetAndVerificationTests(APITestCase):
    def setUp(self):
        self.password = "StrongPassword123!"
        self.user = User.objects.create_user(
            username="secure@example.com",
            email="secure@example.com",
            password=self.password,
            role=UserRole.STUDENT,
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_reset_request_is_generic_for_existing_and_unknown_email(self):
        for email in ("secure@example.com", "unknown@example.com"):
            with self.subTest(email=email):
                response = self.client.post(
                    "/api/auth/password-reset/request/",
                    {"email": email},
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn("If an account exists", response.data["detail"])

    def test_password_reset_changes_password_and_invalidates_token(self):
        refresh = RefreshToken.for_user(self.user)
        token = default_token_generator.make_token(self.user)
        response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {
                "uid": self.uid,
                "token": token,
                "password": "AnotherStrongPassword123!",
                "password_confirm": "AnotherStrongPassword123!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("AnotherStrongPassword123!"))
        refreshed = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": str(refresh)},
        )
        self.assertEqual(refreshed.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_weak_reset_password_is_rejected(self):
        token = default_token_generator.make_token(self.user)
        response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {
                "uid": self.uid,
                "token": token,
                "password": "password",
                "password_confirm": "password",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_verification_is_time_limited_and_reusable_only_once(self):
        token = default_token_generator.make_token(self.user)
        response = self.client.post(
            "/api/auth/verify-email/",
            {"uid": self.uid, "token": token},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        second_response = self.client.post(
            "/api/auth/verify-email/",
            {"uid": self.uid, "token": token},
        )
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)

    def test_invalid_email_verification_token_is_rejected(self):
        response = self.client.post(
            "/api/auth/verify-email/",
            {"uid": self.uid, "token": "invalid-token"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_sends_verification_email_without_exposing_password(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "password": self.password,
                "password_confirm": self.password,
                "role": UserRole.STUDENT,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn(self.password, mail.outbox[0].body)
        self.assertNotIn("password", response.data)
