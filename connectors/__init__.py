import requests
from binascii import b2a_hex
import debugutil

def get_app_connector(app_or_connector):
    from importlib import import_module
    from django.conf import settings

    if isinstance(app_or_connector, str):
        connector_class = app_or_connector
    elif app_or_connector.connector_class:
        connector_class = app_or_connector.connector_class
    else:
        return None

    if connector_class not in settings.CONNECTORS:
        return None

    connector_path = settings.CONNECTORS[connector_class].split('.')
    connector_module = ".".join(connector_path[:-1])
    if connector_module:
        try:
            Connector = getattr(import_module(connector_module),
                connector_path[-1])
        except ImportError:
            return None
        except AttributeError:
            return None
    else:
        try:
            Connector = globals()[connector_path[-1]]
        except KeyError:
            return None
    return Connector

class BaseConnector():
    LOG_NAME = __name__

    @classmethod
    def debug(cls, msg, level=None):
        """
        Prints a debug message when the setting ``DEBUG`` is set to True.
        Each debug message is preprended with the current time provided by
        :func:`datetime.datetime.now` and the class name."

        :param str msg: The debug message to display
        """
        debugutil.debug(msg, category=cls.__name__, logger=cls.LOG_NAME,
                level=level)

    @classmethod
    def debug_http_package(cls, http_package, label=None,
            secret_body_values=None, level=None):
        debugutil.debug_http_package(http_package, label, secret_body_values,
            category=cls.__name__, logger=cls.LOG_NAME, level=level)

    @classmethod
    def is_logged_in(cls, token, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def login(cls, token, credentials, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def signup(cls, token, user, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def get_credentials(cls, user, app_pk):
        from accounts.models import AppAccount
        try:
            credentials = AppAccount.objects.get(
                app__pk=app_pk, user=user)
        except AppAccount.DoesNotExist:
            return None
        else:
            return credentials

    @classmethod
    def get_or_create_credentials(cls, token, user, app_pk):
        credentials = cls.get_credentials(user, app_pk)
        if credentials is None:
            if cls.signup(token, user):
                return cls.get_credentials(user, app_pk)
            else:
                return None
        else:
            return credentials

    @classmethod
    def get_app_script(cls, *args, **kwargs):
        return none

    @classmethod
    def determine_age(cls, user):
        dob = user.profile.date_of_birth
        if dob is not None:
            from datetime import date
            today = date.today()
            return ( today.year - dob.year -
                ((today.month, today.day) < (dob.month, dob.day)) )
        else:
            return None

    @classmethod
    def fetch_and_parse_document(cls, token, url):
        from bs4 import BeautifulSoup
        response = requests.get(cls.route_url(url), params={'token':token})
        return BeautifulSoup(response.text)

    @classmethod
    def get_field_value_from_document(cls, document, field_name):
        field = document.find('input', attrs={"name": field_name})
        return field['value']

    @classmethod
    def form_post(cls, token, url, payload, custom_headers={}):
        from urllib.parse import urlsplit
        urlparts = urlsplit(url)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': '%s://%s' % (urlparts.scheme, urlparts.netloc),
            'User-Agent': (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                "(KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"),
            'Referer': url
        }
        headers.update(custom_headers)
        params = {
            "params": {'token': token},
            "allow_redirects":False,
            "headers": headers,
            "url": cls.route_url(url)
        }
        if "application/json" in headers['Content-Type']:
            params['json'] = payload
        else:
            params['data'] = payload
        return requests.post(**params)

    @classmethod
    def route_url(cls, url):
        from urllib.parse import urlsplit, urlunsplit
        from subdomains.utils import get_domain
        from django.conf import settings
        urlparts = urlsplit(url)
        return urlunsplit((
            settings.ROUTER_PROTOCOL or urlparts.scheme,
            "%s.%s" % (
                b2a_hex(bytes(urlparts.netloc, "utf-8")).decode("utf-8"),
                settings.ROUTER_DOMAIN),
            urlparts.path,
            urlparts.query,
            urlparts.fragment))
