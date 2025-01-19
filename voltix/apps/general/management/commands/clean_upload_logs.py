from django.core.management.base import BaseCommand
from apps.general.models import UploadLog
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Clean upload logs older than 24 hours'

    def handle(self, *args, **kwargs):
        threshold = datetime.now() - timedelta(days=1)
        deleted, _ = UploadLog.objects.filter(timestamp__lt=threshold).delete()
        self.stdout.write(f"Deleted {deleted} upload logs older than 24 hours.")
