from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AccountsUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "email_verified", "is_active", "is_staff")
    list_filter = ("role", "email_verified", "is_active", "is_staff")
    search_fields = ("username", "email")
