from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from voltix.models import InvoiceComparison, Notification, NotificationSettings
from django.contrib.contenttypes.models import ContentType

@shared_task
def send_reminder_to_user(invoice_comparison_id):
    # Recupera la comparación de facturas
    invoice_comparison = InvoiceComparison.objects.get(id=invoice_comparison_id)

    # Verificar si ya se pasó el tiempo de espera (ejemplo: 7 días)
    if invoice_comparison.created_at <= timezone.now() - timedelta(days=7):
        # Verificar si el usuario tiene habilitada la opción de recordatorio
        notification_settings = NotificationSettings.objects.filter(user=invoice_comparison.user).first()
        if notification_settings and notification_settings.enable_reminders:
            message = (
                f"Recuerda que la factura ID {invoice_comparison.invoice.id} tiene discrepancias. "
                f"Hace {invoice_comparison.created_at} que se detectó el problema."
            )
            # Crear una notificación de tipo 'recordatorio'
            Notification.objects.create(
                user=invoice_comparison.user,
                message=message,
                type='recordatorio',
                content_type=ContentType.objects.get_for_model(invoice_comparison),
                object_id=invoice_comparison.id
            )
            print(f"Recordatorio enviado a {invoice_comparison.user.email}")
