from django.apps import AppConfig

class KbConfig(AppConfig):
    name = 'kb'

    def ready(self):
        from .signals import on_role_change
