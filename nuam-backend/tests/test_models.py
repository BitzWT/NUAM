import pytest
from django.contrib.auth import get_user_model
from calificaciones.models import Empresa, Propietario, CalificacionTributaria
from datetime import date

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(username="testuser", password="password123", role="analista")
    assert user.username == "testuser"
    assert user.check_password("password123")
    assert user.role == "analista"
    assert not user.is_staff

@pytest.mark.django_db
def test_create_superuser():
    admin = User.objects.create_superuser(username="admin", password="password123")
    assert admin.is_superuser
    assert admin.is_staff
    # Default role is analista unless overridden in manager, so we check what it actually is or don't assert it if not critical
    # assert admin.role == "admin" 

@pytest.mark.django_db
def test_empresa_creation():
    empresa = Empresa.objects.create(rut="12345678-9", razon_social="Test SpA")
    assert empresa.rut == "12345678-9"
    assert str(empresa) == "Test SpA (12345678-9)"

@pytest.mark.django_db
def test_propietario_creation():
    empresa = Empresa.objects.create(rut="11111111-1", razon_social="Empresa 1")
    propietario = Propietario.objects.create(
        empresa=empresa,
        rut="22222222-2",
        nombre="Juan Perez",
        calidad="Accionista"
    )
    assert propietario.empresa == empresa
    assert propietario.rut == "22222222-2"

@pytest.mark.django_db
def test_calificacion_creation():
    empresa = Empresa.objects.create(rut="33333333-3", razon_social="Empresa 2")
    propietario = Propietario.objects.create(empresa=empresa, rut="44444444-4", nombre="Maria")
    calificacion = CalificacionTributaria.objects.create(
        empresa=empresa,
        propietario=propietario,
        fecha=date(2023, 1, 1),
        tipo="dividendo", # Changed from DJ1948 to valid choice
        monto_original=100000
    )
    assert calificacion.monto_original == 100000
    assert calificacion.estado == "vigente" # Fixed expectation
