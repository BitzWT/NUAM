from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('admin', 'Administrador General'),
        ('tributario', 'Administrador Tributario'),
        ('auditor', 'Auditor Interno'),
        ('corredor', 'Corredor de Bolsa'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='tributario')

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)