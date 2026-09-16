from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserRole


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=(
            (UserRole.STUDENT, UserRole.STUDENT.label),
            (UserRole.PARENT, UserRole.PARENT.label),
            (UserRole.TUTOR, UserRole.TUTOR.label),
        )
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
            "role",
        )
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "email": {"required": True},
        }

    def to_internal_value(self, data):
        forbidden_fields = {
            "is_staff",
            "is_superuser",
            "groups",
            "permissions",
            "user_permissions",
        }
        submitted_forbidden_fields = forbidden_fields.intersection(data.keys())
        if submitted_forbidden_fields:
            errors = {
                field: "This field is not accepted during public registration."
                for field in submitted_forbidden_fields
            }
            raise serializers.ValidationError(errors)
        return super().to_internal_value(data)

    def validate_email(self, value):
        normalized_email = value.strip().lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return normalized_email

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        email = validated_data["email"]

        try:
            return User.objects.create_user(
                username=email,
                password=password,
                **validated_data,
            )
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"email": "An account with this email already exists."}
            ) from exc


class RegistrationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "email_verified")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        return {"user": user}


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].required = False

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=attrs.get("password"),
        )
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        refresh = self.get_token(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
