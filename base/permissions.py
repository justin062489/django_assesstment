from rest_framework import permissions
from rest_framework.exceptions import ValidationError, AuthenticationFailed


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_active and request.user.role == "admin":
            return True
        else:
            raise AuthenticationFailed(detail="Authorized Admin Only", code=401)
