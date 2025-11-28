import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(username, password, role="analista"):
        return User.objects.create_user(username=username, password=password, role=role)
    return _create_user

@pytest.mark.django_db
def test_login_success(api_client, create_user):
    create_user("testuser", "password123")
    response = api_client.post("/api/token/", {
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data

@pytest.mark.django_db
def test_login_failure(api_client):
    response = api_client.post("/api/token/", {
        "username": "wronguser",
        "password": "wrongpassword"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_signup_flow(api_client):
    data = {
        "username": "newuser",
        "email": "new@test.com",
        "password": "newpassword123",
        "role": "analista"
    }
    response = api_client.post("/api/auth/register/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username="newuser").exists()

@pytest.mark.django_db
def test_mfa_setup_requires_auth(api_client):
    response = api_client.get("/api/mfa/setup/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
