from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.general.models import User

import logging

logger = logging.getLogger('django')
class Command(BaseCommand):
    help = 'Elimina usuarios que han sido marcados para eliminación y han estado inactivos por más de 30 días'

    def handle(self, *args, **kwargs):
        limite_fecha = timezone.now() - timedelta(seconds=120)
        usuarios_a_eliminar = User.objects.filter(
            is_active=False,
            deactivation_reason='deletion_pending',  # Solo elimina estos
            updated_at__lt=limite_fecha
        )

        if not usuarios_a_eliminar.exists():
            self.stdout.write(self.style.SUCCESS("No hay usuarios para eliminar."))
            return

        # for user in usuarios_a_eliminar:
        #     self.stdout.write(self.style.WARNING(f"Eliminando usuario: {user.email}"))
        #     user.delete()
        for user in usuarios_a_eliminar:
            self.stdout.write(self.style.WARNING(f"Eliminando usuario: {user.email}"))
        try:
            user.delete()
            logger.info(f"Usuario eliminado: {user.email}")
            self.stdout.write(self.style.SUCCESS(f"Usuario {user.email} eliminado exitosamente."))
        except Exception as e:
            logger.error(f"Error eliminando usuario {user.email}: {e}")
            self.stderr.write(self.style.ERROR(f"Error eliminando {user.email}: {e}"))

        self.stdout.write(self.style.SUCCESS("Proceso de eliminación completado."))
