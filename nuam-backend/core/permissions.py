from rest_framework import permissions

class IsAdminGeneral(permissions.BasePermission):
    """
    Administrador General: Operates the complete system.
    Access to users, companies, DJs, ratings.
    """
    def has_permission(self, request, view):
        # Superuser always has access, or role='admin'
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)

class IsAdminTributario(permissions.BasePermission):
    """
    Administrador Tributario: Specialized tax role.
    Validates parsing, approves ratings, edits tax params.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['tributario', 'admin'] or request.user.is_superuser

class IsAuditorInterno(permissions.BasePermission):
    """
    Auditor Interno: Read-only access.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'auditor':
            return request.method in permissions.SAFE_METHODS
        return request.user.role in ['admin', 'tributario'] or request.user.is_superuser

class IsCorredor(permissions.BasePermission):
    """
    Corredor: Read-only access to assigned companies.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Corredor needs to create/edit companies they manage.
        # We rely on 'has_object_permission' and 'get_queryset' for restrictions.
        if request.user.role == 'corredor':
            return True 
        return True 

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role in ['admin', 'tributario', 'auditor']:
            return True
        if request.user.role == 'corredor':
            empresa = None
            if hasattr(obj, 'empresas'): 
                pass 
            elif hasattr(obj, 'empresa'): 
                empresa = obj.empresa
            elif hasattr(obj, 'razon_social'): 
                empresa = obj
            
            if empresa:
                if hasattr(request.user, 'corredor_profile'):
                    return request.user.corredor_profile.empresas.filter(pk=empresa.pk).exists()
            return False
        return False
