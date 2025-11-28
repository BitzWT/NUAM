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
    return User.objects.create_user(username="admin", password="password", role="admin")

@pytest.fixture
def analista_user():
    return User.objects.create_user(username="analista", password="password", role="analista")

@pytest.fixture
def auth_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.mark.django_db
def test_create_empresa_admin(auth_client):
    data = {"rut": "99999999-9", "razon_social": "Test Corp"}
    response = auth_client.post("/api/empresas/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Empresa.objects.count() == 1

@pytest.mark.django_db
def test_get_empresas_unauthenticated(api_client):
    response = api_client.get("/api/empresas/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_user_management_admin_only(api_client, analista_user, admin_user):
    # Analista tries to list users -> Forbidden (assuming IsAdmin permission)
    api_client.force_authenticate(user=analista_user)
    response = api_client.get("/api/users/")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Admin tries to list users -> OK
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/users/")
    assert response.status_code == status.HTTP_200_OK
