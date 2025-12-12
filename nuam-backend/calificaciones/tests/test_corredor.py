from django.test import TestCase
from django.contrib.auth import get_user_model
from calificaciones.models import Empresa, Corredor, CalificacionTributaria, Propietario
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

User = get_user_model()

class CorredorTests(TestCase):
    def setUp(self):
        # Create Users
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.corredor_user = User.objects.create_user('corredor', 'corredor@test.com', 'password', role='corredor')
        self.other_user = User.objects.create_user('other', 'other@test.com', 'password', role='analista')

        # Create Companies
        self.empresa_a = Empresa.objects.create(rut='11.111.111-1', razon_social='Empresa A')
        self.empresa_b = Empresa.objects.create(rut='22.222.222-2', razon_social='Empresa B')

        # Create Corredor Profile
        self.corredor_profile = Corredor.objects.create(
            user=self.corredor_user,
            rut='99.999.999-9',
            empresa_corredora='Corredora XYZ'
        )
        self.corredor_profile.empresas.add(self.empresa_a)

        # Create Data
        self.propietario = Propietario.objects.create(empresa=self.empresa_a, rut='33.333.333-3', nombre='Prop A')
        self.calif_a = CalificacionTributaria.objects.create(
            empresa=self.empresa_a,
            propietario=self.propietario,
            fecha=date(2023, 1, 1),
            tipo='retiro',
            monto_original=1000
        )
        
        self.propietario_b = Propietario.objects.create(empresa=self.empresa_b, rut='44.444.444-4', nombre='Prop B')
        self.calif_b = CalificacionTributaria.objects.create(
            empresa=self.empresa_b,
            propietario=self.propietario_b,
            fecha=date(2023, 1, 1),
            tipo='retiro',
            monto_original=2000
        )

        self.client = APIClient()

    def test_corredor_can_see_assigned_company_calificaciones(self):
        self.client.force_authenticate(user=self.corredor_user)
        response = self.client.get('/api/calificaciones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.calif_a.id)

    def test_corredor_cannot_see_unassigned_company_calificaciones(self):
        self.client.force_authenticate(user=self.corredor_user)
        # Should not see calif_b
        response = self.client.get('/api/calificaciones/')
        ids = [c['id'] for c in response.data]
        self.assertNotIn(self.calif_b.id, ids)

    def test_corredor_me_endpoint(self):
        self.client.force_authenticate(user=self.corredor_user)
        response = self.client.get('/api/corredores/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['empresa_corredora'], 'Corredora XYZ')
        self.assertIn(self.empresa_a.id, response.data['empresas'])

    def test_admin_can_see_all(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/calificaciones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
