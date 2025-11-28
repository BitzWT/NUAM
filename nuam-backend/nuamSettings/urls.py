"""
URL configuration for nuamSettings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from calificaciones.views import health
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from calificaciones.views import CalificacionTributariaViewSet, EmpresaViewSet, PropietarioViewSet, AuditoriaViewSet, Certificado70ViewSet, AccionViewSet

from core.user_views import UserViewSet

router = DefaultRouter()
router.register("calificaciones", CalificacionTributariaViewSet, basename="calificaciones")
router.register("empresas", EmpresaViewSet, basename="empresas")
router.register("propietarios", PropietarioViewSet, basename="propietarios")
router.register("auditoria", AuditoriaViewSet, basename="auditoria")
router.register("users", UserViewSet, basename="users")
router.register("certificados70", Certificado70ViewSet, basename="certificados70")
router.register("acciones", AccionViewSet, basename="acciones")

from django.urls import path, include

from core.mfa_views import SetupMFAView, VerifyMFAView, LoginMFAView, LoginVerifyView
from calificaciones.bulk_upload_views import BulkUploadView
from core.register_view import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health),
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    
    # Auth Endpoints
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", LoginMFAView.as_view()),
    path("api/auth/login/verify/", LoginVerifyView.as_view()),

    # MFA Endpoints
    path("api/mfa/setup/", SetupMFAView.as_view()),
    path("api/mfa/verify/", VerifyMFAView.as_view()),

    # Bulk Upload
    path("api/calificaciones/upload/", BulkUploadView.as_view()),

    path("api/", include(router.urls)),
]


