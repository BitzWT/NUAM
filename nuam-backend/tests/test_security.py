import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from calificaciones.models import Empresa

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user():
    return User.objects.create_user(username="admin_sec", password="password", role="admin")

@pytest.fixture
def auth_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.mark.django_db
def test_xss_protection_in_creation(auth_client):
    """
    Test that injecting a script tag into a field does not execute.
    Note: Django REST Framework + React usually sanitizes this on display, 
    but we check that the API accepts it as text or rejects it depending on validation.
    Here we check that it's stored as-is (Django doesn't strip by default) 
    but we rely on frontend to escape. 
    However, for a stricter backend test, we might want to check if we have a validator.
    For this test, we just verify it doesn't crash and stores the string.
    """
    xss_payload = "<script>alert('XSS')</script>"
    data = {"rut": "55555555-5", "razon_social": xss_payload}
    
    response = auth_client.post("/api/empresas/", data)
    assert response.status_code == status.HTTP_201_CREATED
    
    empresa = Empresa.objects.get(rut="55555555-5")
    assert empresa.razon_social == xss_payload
    # The security relies on the Frontend (React) escaping this. 
    # If we wanted backend sanitization, we'd need a library like bleach.

@pytest.mark.django_db
def test_sql_injection_protection(auth_client):
    """
    Test that SQL injection payloads in search parameters don't leak data.
    Django ORM prevents this by default.
    """
    # Create some data
    Empresa.objects.create(rut="11111111-1", razon_social="Safe Corp")
    
    # Payload that would return all rows if injected into raw SQL: ' OR '1'='1
    sqli_payload = "' OR '1'='1"
    
    response = auth_client.get(f"/api/empresas/?search={sqli_payload}")
    assert response.status_code == status.HTTP_200_OK
    
    # Should NOT return everything if the search logic is correct (filtering by name/rut)
    # Since "Safe Corp" doesn't match the payload, it should return empty or just matching text.
    # If SQLi worked, it might ignore the filter.
    assert len(response.data) == 0

@pytest.mark.django_db
def test_csrf_protection_enforced(api_client):
    """
    Test that non-safe methods require CSRF if using SessionAuth, 
    but since we use JWT, we check that unauthenticated requests are rejected.
    """
    data = {"rut": "66666666-6", "razon_social": "Hacker Corp"}
    response = api_client.post("/api/empresas/", data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
