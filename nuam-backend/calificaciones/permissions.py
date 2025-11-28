from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class IsAuditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "auditor"

class IsAnalista(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["analista", "admin"]
