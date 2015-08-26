from django.apps import AppConfig

class CustomConfig(AppConfig):
    name = 'services.usermanagement'
    verbose_name = 'User Management'

    def ready(self):
        import services.usermanagement.signals

