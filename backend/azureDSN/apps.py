from django.apps import AppConfig


class AzuredsnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'azureDSN'
    
    def ready(self):
        import azureDSN.utils.signal
