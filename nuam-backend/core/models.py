from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('analista', 'Analista Tributario'),
        ('editor', 'Usuario Autorizado (Editor)'),
        ('auditor', 'Auditor'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='analista')

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)