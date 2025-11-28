from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import CalificacionTributaria, Auditoria
from .serializers import CalificacionTributariaSerializer

@receiver(pre_save, sender=CalificacionTributaria)
def before_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._antes = CalificacionTributariaSerializer(sender.objects.get(pk=instance.pk)).data
        except sender.DoesNotExist:
            instance._antes = None

@receiver(post_save, sender=CalificacionTributaria)
def after_update(sender, instance, created, **kwargs):
    Auditoria.objects.create(
        usuario=instance.creado_por, # Note: This attributes action to creator, ideally should be current user
        accion="crear" if created else "modificar",
        entidad="CalificacionTributaria",
        entidad_id=instance.pk,
        detalle={
            "antes": getattr(instance, "_antes", None),
            "despues": CalificacionTributariaSerializer(instance).data
        }
    )

@receiver(post_delete, sender=CalificacionTributaria)
def after_delete(sender, instance, **kwargs):
    try:
        Auditoria.objects.create(
            usuario=instance.creado_por,
            accion="eliminar",
            entidad="CalificacionTributaria",
            entidad_id=instance.pk,
            detalle={
                "antes": CalificacionTributariaSerializer(instance).data,
                "despues": None
            }
        )
    except Exception as e:
        print(f"Error creating audit for deletion: {e}")
