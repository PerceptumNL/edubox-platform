from bs4 import BeautifulSoup

from router import utils

class BaseAdaptor():

    @classmethod
    def debug(cls, msg):
        """
        Prints a debug message when the setting ``DEBUG`` is set to True.
        Each debug message is preprended with the current time provided by
        :func:`datetime.datetime.now` and the class name."

        :param str msg: The debug message to display
        """
        utils.debug(msg, category=cls.__name__)

    @classmethod
    def debug_http_package(cls, http_package, label=None, secret_body_values=None):
        utils.debug_http_package(http_package, label, secret_body_values,
            category=cls.__name__)

    @classmethod
    def is_logged_in(cls, user, session, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def login(cls, credentials, user, session, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def signup(cls, user, session, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fetch_and_parse_document(cls, session, url):
        response = session.request(method="GET", url=url)
        return BeautifulSoup(response.text)

    @classmethod
    def get_field_value_from_document(cls, document, field_name):
        field = document.find('input', attrs={"name": field_name})
        return field['value']

    @classmethod
    def form_post(cls, session, url, payload, custom_headers={}):
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
            "method":"POST",
            "allow_redirects":False,
            "headers": headers,
            "url": url
        }
        if headers['Content-Type'] == "application/json":
            params['json'] = payload
        else:
            params['data'] = payload
        return session.request(**params)


class CodeOrgAdaptor(BaseAdaptor):
    LOGIN_CHECK_URL = "https://studio.code.org/users/edit"
    LOGIN_PAGE_URL = "https://studio.code.org/users/sign_in"
    LOGIN_URL = "https://studio.code.org/users/sign_in"
    SECTION_LOGIN_PAGE_URL = "https://studio.code.org/sections/%s"
    SECTION_LOGIN_URL = "https://studio.code.org/sections/%s/log_in"


    @classmethod
    def is_logged_in(cls, user, session, *args, **kwargs):
        response = session.request(method="HEAD",
                                   url=cls.LOGIN_CHECK_URL,
                                   allow_redirects=False)
        return response.status_code == 302

    @classmethod
    def login(cls, credentials, user, session, *args, **kwargs):
        secret_body_values = [credentials.username, credentials.password]
        params = credentials.parameters or {"login_mode": "normal"}
        if params['login_mode'] == "normal":
            cls.debug('Login mode: normal')
            login_document = cls.fetch_and_parse_document(
                session, cls.LOGIN_PAGE_URL)
            authenticity_token = cls.get_field_value_from_document(
                login_document, "authenticity_token")
            payload = {
                "user[login]": credentials.username,
                "user[password]": credentials.password,
                "utf8": "\u2713",
                "authenticity_token": authenticity_token,
                "user[remember_me]": "1",
                "user[hashed_email]": "",
                "commit": "Sign in"
            }
            login_response = cls.form_post(session, cls.LOGIN_URL, payload)
        elif params['login_mode'] == "class":
            cls.debug('Login mode: class')
            if 'section' not in params:
                return False
            login_document = cls.fetch_and_parse_document(
                session, cls.SECTION_LOGIN_PAGE_URL % (params['section'],))
            authenticity_token = cls.get_field_value_from_document(
                login_document, "authenticity_token")
            payload = {
                "user_id": credentials.username,
                "secret_words": credentials.password,
                "utf8": "\u2713",
                "authenticity_token": authenticity_token,
                "secret_picture_id": "",
                "button": ""
            }
            login_response = cls.form_post(
                session=session,
                url=cls.SECTION_LOGIN_URL % (params['section'],),
                payload=payload,
                custom_headers={
                    'Referer': cls.SECTION_LOGIN_PAGE_URL % (
                        params['section'],)
                })
        else:
            cls.debug('Unknown login mode')
            return False

        cls.debug_http_package(login_response.request, label='Login request',
                secret_body_values=secret_body_values)
        cls.debug_http_package(login_response, label='Login response')

        return login_response.status_code == 302

    @classmethod
    def signup(cls, user, session, *args, **kwargs):
        raise NotImplementedError()
