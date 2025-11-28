import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from calificaciones.models import Empresa, Propietario, CalificacionTributaria, Certificado70
from datetime import date
import os

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client):
    user = User.objects.create_user(username="cert_user", password="password", role="editor")
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
def test_generate_certificado_70(auth_client):
    # Setup Data
    empresa = Empresa.objects.create(rut="70707070-7", razon_social="Empresa Cert70")
    propietario = Propietario.objects.create(empresa=empresa, rut="80808080-8", nombre="Socio Cert70")
    
    CalificacionTributaria.objects.create(
        empresa=empresa,
        propietario=propietario,
        fecha=date(2023, 5, 1),
        tipo="retiro",
        monto_original=1000000,
        estado="vigente"
    )

    # Call Generate Endpoint
    data = {
        "empresa_id": empresa.id,
        "propietario_id": propietario.id,
        "anio": 2023
    }
    response = auth_client.post("/api/certificados70/generar/", data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["anio_comercial"] == 2023
    assert response.data["archivo_pdf"] is not None
    
    # Verify Model Created
    cert = Certificado70.objects.get(empresa=empresa, propietario=propietario, anio_comercial=2023)
    assert cert.totales["monto_historico"] == 1000000
    assert os.path.exists(cert.archivo_pdf)

    # Cleanup PDF
    if os.path.exists(cert.archivo_pdf):
        os.remove(cert.archivo_pdf)
