from django.apps import AppConfig


class VoltixConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.general'
    
    def ready(self):
        import apps.general.signals

    def ready(self):
        print("VoltixConfig ready() called")
        import apps.general.signals

