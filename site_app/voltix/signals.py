from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import User, Profile, InvoiceComparison, Notification, NotificationSettings
from notifications.tasks import send_reminder_to_user

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
            photo_url=""
        )
        # Crear configuraciones de notificaciones predeterminadas
        NotificationSettings.objects.create(
            user=instance,
            enable_alerts=True,
            enable_recommendations=True,
            enable_reminders=True
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Guardar automáticamente el perfil asociado cuando el usuario se guarda
    instance.profile.save()


@receiver(post_save, sender=InvoiceComparison)
def create_notification_for_discrepancies(sender, instance, created, **kwargs):
    if created and not instance.is_comparison_valid:
        # Verificar si el usuario tiene habilitadas las notificaciones de tipo 'alerta'
        notification_settings = NotificationSettings.objects.filter(user=instance.user).first()
        if notification_settings and notification_settings.enable_alerts:
            # Mensaje de notificación
            message = (
                f"Detectamos que la factura ID {instance.invoice.id} presenta discrepancias con los datos internos del sistema"
            )
            # Crear la notificación genérica
            Notification.objects.create(
                user=instance.user,
                message=message,
                type='alerta',
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )
            # Programar el recordatorio para dentro de 7 días
            send_reminder_to_user.apply_async((instance.id,), countdown=7*24*60*60)  # 7 días en segundos