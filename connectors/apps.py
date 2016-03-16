from django.apps import AppConfig
import logging
logger = logging.getLogger(__name__)

class ConnectorsConfig(AppConfig):
    name = 'connectors'

    def ready(self):
        from connectors import get_app_connector
        from django.conf import settings

        logger.info('Registering signals for connectors: %s' %
                (settings.CONNECTORS,))
        connectors = [ get_app_connector(con) for con in settings.CONNECTORS ]
        for connector in connectors:
            if connector:
                connector.register_signals()
