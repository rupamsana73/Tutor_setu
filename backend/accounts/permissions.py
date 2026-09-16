from rest_framework.permissions import BasePermission


class HasApplicationRole(BasePermission):
    allowed_roles = frozenset()

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsTutor(HasApplicationRole):
    allowed_roles = frozenset({"tutor"})


class IsStudentOrParent(HasApplicationRole):
    allowed_roles = frozenset({"student", "parent"})


class IsApplicationAdmin(HasApplicationRole):
    allowed_roles = frozenset({"admin"})
