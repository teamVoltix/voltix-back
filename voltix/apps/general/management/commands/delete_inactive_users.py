from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.general.models import User

class Command(BaseCommand):
    help = 'Elimina usuarios que han sido marcados para eliminación y han estado inactivos por más de 30 días'

    def handle(self, *args, **kwargs):
        limite_fecha = timezone.now() - timedelta(seconds=30)
        usuarios_a_eliminar = User.objects.filter(
            is_active=False,
            deactivation_reason='deletion_pending',  # Solo elimina estos
            updated_at__lt=limite_fecha
        )

        for user in usuarios_a_eliminar:
            self.stdout.write(self.style.WARNING(f"Eliminando usuario: {user.email}"))
            user.delete()

        self.stdout.write(self.style.SUCCESS("Proceso de eliminación completado."))
