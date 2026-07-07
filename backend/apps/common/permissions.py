from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and get_user_role(request.user) == "student")


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and get_user_role(request.user) == "teacher")


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and get_user_role(request.user) == "admin")


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None) or getattr(obj, "student", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and (get_user_role(request.user) == "admin" or owner == request.user)
        )


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


def get_user_role(user):
    if getattr(user, "is_superuser", False):
        return "admin"
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", None)
