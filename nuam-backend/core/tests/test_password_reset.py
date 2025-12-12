from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword'
        )
        self.request_url = '/api/auth/password-reset/'
        self.confirm_url = '/api/auth/password-reset/confirm/'

    def test_request_password_reset(self):
        response = self.client.post(self.request_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('test@example.com', mail.outbox[0].to)
        self.assertIn('Password Reset Request', mail.outbox[0].subject)

    def test_request_password_reset_invalid_email(self):
        # Even if email doesn't exist, we return 200 OK
        response = self.client.post(self.request_url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # But no email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_confirm_password_reset(self):
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        data = {
            'uid': uid,
            'token': token,
            'password': 'newpassword123'
        }
        response = self.client.post(self.confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_confirm_password_reset_invalid_token(self):
        token = 'invalidtoken'
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        data = {
            'uid': uid,
            'token': token,
            'password': 'newpassword123'
        }
        response = self.client.post(self.confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
