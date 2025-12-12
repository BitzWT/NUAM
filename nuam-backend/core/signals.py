from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from calificaciones.models import Corredor

User = get_user_model()

@receiver(post_save, sender=User)
def create_corredor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'corredor':
        # Create empty profile. 
        # Note: rut and empresa_corredora are required fields but for auto-creation we might need defaults
        # or we accept empty strings if permitted by model (checked: max_length defined but no null=True, implies required).
        # We should set placeholders.
        Corredor.objects.get_or_create(
            user=instance,
            defaults={
                'rut': 'SIN-RUT', 
                'empresa_corredora': f'Corredora {instance.username}'
            }
        )
