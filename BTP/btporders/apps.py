from django.apps import AppConfig


class BtpordersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'btporders'

    
    def ready(self):
        from . import dbsignal
