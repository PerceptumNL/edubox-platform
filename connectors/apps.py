from django.apps import AppConfig

class ConnectorsConfig(AppConfig):
    name = 'connectors'

    def ready(self):
        from connectors import get_app_connector
        from django.conf import settings
        from debugutil import debug

        connectors = [ get_app_connector(con) for con in settings.CONNECTORS ]
        for connector in connectors:
            if connector:
                connector.register_signals()
