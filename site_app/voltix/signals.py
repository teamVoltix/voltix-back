from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile
from datetime import date  # Importamos para usar una fecha predeterminada

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print(f"Creating profile for user {instance.id}")
        # Crear un perfil automáticamente con valores predeterminados
        Profile.objects.create(
            user=instance,
            birth_date=None, 
            address="",
            phone_number="",
            preferences={}  # Vacío por defecto
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Guardar automáticamente el perfil asociado cuando el usuario se guarda
    instance.profile.save()
