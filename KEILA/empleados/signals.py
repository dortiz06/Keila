from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from datetime import date
from .models import Perfil # Importar Perfil desde el mismo módulo

User = get_user_model()

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        # Solo crear perfil si no existe
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(
                usuario=instance,
                tipo_perfil='EMPLEADO',  # Default
                fecha_contratacion=date.today(),
                numero_empleado=f"EMP{instance.id:04d}",
                puesto="Por definir"
            )
