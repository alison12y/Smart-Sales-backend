from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Cliente(models.Model):
    # Ahora permite varios clientes por usuario
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clientes'
    )
    ci_nit = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=150, blank=True)
    ciudad = models.CharField(max_length=50, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        full_name = self.user.get_full_name()
        if full_name:
            return full_name
        return self.user.username or self.user.email or f"Cliente {self.pk}"


# Crea un cliente automático al registrar un nuevo usuario normal
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_cliente_for_user(sender, instance, created, **kwargs):
#    if created and not instance.is_staff:
#       Cliente.objects.create(user=instance)