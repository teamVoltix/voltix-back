from __future__ import absolute_import, unicode_literals
import multiprocessing
multiprocessing.set_start_method('forkserver', force=True)

import os
from celery import Celery

# Establece el módulo de configuración de Django como predeterminado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_app.settings')

# Crea la aplicación de Celery
app = Celery('site_app', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Configura Celery para leer las configuraciones desde el archivo settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks para buscar automáticamente en los tasks.py de las apps registradas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# from notifications.tasks import send_test_reminder
# send_test_reminder.apply_async(args=[4], countdown=60)