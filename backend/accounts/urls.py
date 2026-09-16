from django.urls import path

from .views import (
    CurrentUserView,
    EmailTokenView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    RegistrationView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    EmailVerificationView,
    ResendVerificationView,
)


urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/", EmailTokenView.as_view(), name="token"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("password-reset/request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("verify-email/", EmailVerificationView.as_view(), name="verify-email"),
    path("verify-email/resend/", ResendVerificationView.as_view(), name="verify-email-resend"),
]
