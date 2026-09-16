from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.conf import settings
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .serializers import (
    EmailTokenObtainPairSerializer,
    LoginSerializer,
    RegistrationResponseSerializer,
    RegistrationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    authentication_classes = ()
    permission_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.email_verified = False
        user.save(update_fields=("email_verified",))
        _send_verification_email(user)
        response_serializer = RegistrationResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = ()
    permission_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as exc:
            if set(exc.detail) == {"detail"}:
                return Response(
                    {"detail": "Invalid email or password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            raise
        response_serializer = RegistrationResponseSerializer(serializer.validated_data["user"])
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class EmailTokenView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "token"


class RefreshTokenView(TokenRefreshView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "refresh"


class LogoutView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        token = request.data.get("refresh")
        if not token:
            return Response({"detail": "Refresh token is required."}, status=400)
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            return Response({"detail": "Invalid refresh token."}, status=400)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RegistrationResponseSerializer

    def get_object(self):
        return self.request.user


def _send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    send_mail(
        "Verify your TutorSetu email",
        f"Verify your email at {settings.FRONTEND_URL}/verify-email?uid={uid}&token={token}.",
        None,
        [user.email],
    )


def _blacklist_user_refresh_tokens(user):
    for outstanding in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=outstanding)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    authentication_classes = ()
    permission_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_model().objects.filter(
            email__iexact=serializer.validated_data["email"],
            is_active=True,
        ).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_mail(
                "Reset your TutorSetu password",
                f"Reset your password at {settings.FRONTEND_URL}/password-reset/confirm?uid={uid}&token={token}.",
                None,
                [user.email],
            )
        return Response(
            {"detail": "If an account exists for that email, reset instructions have been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    authentication_classes = ()
    permission_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user_id = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = get_user_model().objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            raise serializers.ValidationError({"detail": "Invalid or expired reset token."})
        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            raise serializers.ValidationError({"detail": "Invalid or expired reset token."})
        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=("password",))
        _blacklist_user_refresh_tokens(user)
        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)


class EmailVerificationView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        uid = request.data.get("uid")
        token = request.data.get("token")
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = get_user_model().objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            raise serializers.ValidationError({"detail": "Invalid or expired verification token."})
        if user.email_verified:
            return Response({"detail": "Email is already verified."}, status=status.HTTP_200_OK)
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"detail": "Invalid or expired verification token."})
        user.email_verified = True
        user.save(update_fields=("email_verified",))
        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)


class ResendVerificationView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    authentication_classes = ()
    permission_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_model().objects.filter(
            email__iexact=serializer.validated_data["email"],
            is_active=True,
            email_verified=False,
        ).first()
        if user:
            _send_verification_email(user)
        return Response(
            {"detail": "If an account exists and is unverified, verification instructions have been sent."},
            status=status.HTTP_200_OK,
        )
