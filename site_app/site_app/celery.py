from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establece el módulo de configuración de Django como predeterminado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_app.settings')

# Crea la aplicación de Celery
app = Celery('site_app')

# Configura Celery para leer las configuraciones desde el archivo settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks para buscar automáticamente en los tasks.py de las apps registradas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
