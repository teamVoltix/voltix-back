from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from apps.general.models import InvoiceComparison, Notification, NotificationSettings, User
from django.contrib.contenttypes.models import ContentType


@shared_task
def send_reminder_to_user(invoice_comparison_id):
    # Recuperar la comparación de facturas
    try:
        invoice_comparison = InvoiceComparison.objects.get(id=invoice_comparison_id)
    except InvoiceComparison.DoesNotExist:
        print(f"No se encontró la comparación de factura con ID {invoice_comparison_id}")
        return  # Detener la tarea si no se encuentra la comparación

    # Verificar si ya ha pasado más de 5 minuto desde la creación de la comparación
    if invoice_comparison.created_at <= timezone.now() - timedelta(minutes=1):
        # Recuperar la configuración de notificaciones del usuario relacionado
        notification_settings = NotificationSettings.objects.filter(user=invoice_comparison.user).first()

        if notification_settings and notification_settings.enable_reminders:
            # Crear el mensaje de recordatorio
            message = (
                f"Recuerda que la factura ID {invoice_comparison.invoice.id} tiene discrepancias. "
                f"Hace {timezone.now() - invoice_comparison.created_at} que se detectó el problema."
            )

            # Crear una nueva notificación de tipo 'recordatorio' en la base de datos
            Notification.objects.create(
                user=invoice_comparison.user,
                message=message,
                type='recordatorio',
                content_type=ContentType.objects.get_for_model(invoice_comparison),
                object_id=invoice_comparison.id
            )
            print(f"Recordatorio guardado para {invoice_comparison.user.email}")
        else:
            print(f"El usuario {invoice_comparison.user.email} no tiene habilitado los recordatorios.")
    else:
        print(f"El recordatorio no se guardó porque aún no han pasado 5 minutos desde la creación de la comparación.")



# simulacion
@shared_task
def send_test_reminder(user_id):
    # Simular envío de un recordatorio
    try:
        user = User.objects.get(user_id=user_id)  # Obtener el objeto usuario
        message = f"Prueba de recordatorio para {user.email}"
        
        # Crear la notificación para la prueba
        Notification.objects.create(
            user=user,
            message=message,
            type='recordatorio',
            content_type=ContentType.objects.get_for_model(User),  # Relaciona el tipo de modelo (User)
            object_id=user.id
        )
        print(f"Prueba de recordatorio guardada para {user.email}")
    except User.DoesNotExist:
        print(f"No se encontró el usuario con user_id={user_id}")
