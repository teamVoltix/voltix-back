from django.core.management.base import BaseCommand
from django.utils.timezone import now
from apps.general.models import Notification, ReminderSchedule
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Process scheduled reminders and create notifications"

    def handle(self, *args, **kwargs):
        # Fetch reminders that are due to be created
        reminders_due = ReminderSchedule.objects.filter(scheduled_time__lte=now())

        for reminder in reminders_due:
            # Create the reminder notification
            message = (
                f"Reminder: Invoice ID {reminder.invoice_comparison.invoice.id} has discrepancies. "
                f"Detected {now() - reminder.invoice_comparison.created_at} ago."
            )
            Notification.objects.create(
                user=reminder.user,
                message=message,
                type='recordatorio',
                content_type=ContentType.objects.get_for_model(reminder.invoice_comparison),
                object_id=reminder.invoice_comparison.id
            )
            self.stdout.write(f"Reminder created for {reminder.user.email}")

        # Delete processed reminders
        reminders_due.delete()
        self.stdout.write(f"Processed {len(reminders_due)} reminders.")
