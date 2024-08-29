from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Позволяет редактировать только автору/админу."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or (
            request.method in permissions.SAFE_METHODS
        ):
            return True
        return obj.author == request.user
