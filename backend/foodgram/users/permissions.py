from rest_framework.permissions import BasePermission

from .models import CustomUser


class IsBlockPermission(BasePermission):
    def has_permission(self, request, view):
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email)
        return not user[0].is_blocked
