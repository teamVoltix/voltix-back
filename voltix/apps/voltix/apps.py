from django.apps import AppConfig


class VoltixConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.voltix'
    
    def ready(self):
        import apps.voltix.signals

    def ready(self):
        print("VoltixConfig ready() called")
        import apps.voltix.signals

