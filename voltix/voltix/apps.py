from django.apps import AppConfig


class VoltixConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voltix'
    
    def ready(self):
        import voltix.signals

    def ready(self):
        print("VoltixConfig ready() called")
        import voltix.signals

