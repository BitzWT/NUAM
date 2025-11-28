from rest_framework import permissions

class IsAnalista(permissions.BasePermission):
    """
    Allows access to Analistas and Editors (since Editors are Analistas + more).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['analista', 'editor', 'admin']

class IsEditor(permissions.BasePermission):
    """
    Allows access only to Editors and Admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['editor', 'admin']

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to Admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)

class IsAuditor(permissions.BasePermission):
    """
    Allows access to Auditors (Read-only usually).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'auditor'
