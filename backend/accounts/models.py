from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    STUDENT = "student", "Student"
    PARENT = "parent", "Parent"
    TUTOR = "tutor", "Tutor"
    ADMIN = "admin", "Admin"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
    )

    @property
    def is_student(self):
        return self.role == UserRole.STUDENT

    @property
    def is_parent(self):
        return self.role == UserRole.PARENT

    @property
    def is_tutor(self):
        return self.role == UserRole.TUTOR

    @property
    def is_admin_role(self):
        return self.role == UserRole.ADMIN

    def __str__(self):
        return self.username
