import pytest
import pandas as pd
import io
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from calificaciones.models import CalificacionTributaria

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client):
    user = User.objects.create_user(username="uploader", password="password", role="editor")
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
def test_bulk_upload_success(auth_client):
    # Create a dummy Excel file
    data = {
        'rut_empresa': ['11111111-1'],
        'razon_social': ['Empresa Bulk'],
        'rut_propietario': ['22222222-2'],
        'nombre_propietario': ['Propietario Bulk'],
        'fecha': ['2023-01-01'],
        'tipo_calificacion': ['DJ1948'],
        'monto': [500000]
    }
    df = pd.DataFrame(data)
    file_obj = io.BytesIO()
    df.to_excel(file_obj, index=False)
    file_obj.seek(0)
    file_obj.name = "test.xlsx"

    response = auth_client.post(
        "/api/calificaciones/upload/",
        {"file": file_obj},
        format="multipart"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["created"] == 1
    assert CalificacionTributaria.objects.count() == 1

@pytest.mark.django_db
def test_bulk_upload_missing_columns(auth_client):
    # Create Excel with missing columns
    data = {'wrong_col': [1]}
    df = pd.DataFrame(data)
    file_obj = io.BytesIO()
    df.to_excel(file_obj, index=False)
    file_obj.seek(0)
    file_obj.name = "bad.xlsx"

    response = auth_client.post(
        "/api/calificaciones/upload/",
        {"file": file_obj},
        format="multipart"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Missing columns" in response.data["error"]
