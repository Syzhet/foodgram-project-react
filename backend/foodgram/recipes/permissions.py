from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorOrAuthOrRead(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        return obj.author == request.user or request.user.is_superuser
