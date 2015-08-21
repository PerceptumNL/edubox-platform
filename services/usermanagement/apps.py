from django.app import AppConfig

class CustomConfig(AppConfig):
    name = 'usermanagement'
    verbose_name = 'User Management'

    def ready(self):
        import services.usermanagement.signals

