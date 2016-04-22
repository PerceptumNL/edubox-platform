"""Module containing connector class for Trello.com"""
import requests

from connectors import BaseConnector
from kb.helpers import create_token, unpack_token

class Connector(BaseConnector):
    """Connector class for Trello.com"""
    LOG_NAME = __name__
    HOME_PAGE = "https://trello.com"
    SIGNUP_PAGE = HOME_PAGE+"/signup"
    SIGNUP_URL = HOME_PAGE+"/1/signup"
    LOGIN_CHECK_URL = HOME_PAGE+"/announcements"
    LOGIN_PAGE = HOME_PAGE+"/login"
    LOGIN_STEP1_URL = HOME_PAGE+"/1/authentication"
    LOGIN_STEP2_URL = HOME_PAGE+"/1/authorization/session"

    @classmethod
    def is_logged_in(cls, token, *args, **kwargs):
        """Returns True if user is still logged in."""
        response = requests.head(cls.route_url(cls.LOGIN_CHECK_URL),
                                 params={'token': token},
                                 allow_redirects=False)
        if response.status_code != 401:
            cls.debug(114, token=token)
            return True
        else:
            return False

    @classmethod
    def login(cls, token, credentials, *args, **kwargs):
        from accounts.models import AppAccount
        if not isinstance(credentials, AppAccount):
            cls.debug(512)
            cls.debug(113, token=token)
            return False

        try:
            dsc_token = cls.get_regex_match_from_url(
                token, cls.LOGIN_PAGE, r'.*window.dsc="([^"]+)";.*').group(1)
        except AttributeError:
            cls.debug(510, field="window.dsc")
            cls.debug(113, token=token)
            return False

        payload = {
            "method": "password",
            "factors[user]": credentials.username,
            "factors[password]": credentials.password,
        }
        secret_body_values = [credentials.username, credentials.password]
        login_step1_response = cls.form_post(
            token=token,
            url=cls.LOGIN_STEP1_URL,
            payload=payload,
            custom_headers={
                'Referer': cls.LOGIN_PAGE})
        cls.debug_http_package(login_step1_response.request,
                               label='Login request (step 1)',
                               secret_body_values=secret_body_values)
        cls.debug_http_package(login_step1_response,
                               label='Login response (step 1)')

        if login_step1_response.status_code == 200:
            try:
                authentication_code = login_step1_response.json()['code']
            except (ValueError, KeyError):
                cls.debug(513, var='code')
                cls.debug(113, token=token)
                return False

            payload = {
                "authentication": authentication_code,
                "dsc": dsc_token,
            }

            login_step2_response = cls.form_post(
                token=token,
                url=cls.LOGIN_STEP2_URL,
                payload=payload,
                custom_headers={
                    'Referer': cls.LOGIN_PAGE})
            cls.debug_http_package(login_step2_response.request,
                                   label='Login request (step 2)',
                                   secret_body_values=secret_body_values)
            cls.debug_http_package(login_step2_response,
                                   label='Login response (step 2)')

            if login_step2_response.status_code == 204:
                cls.debug(112, token=token)
                return True
            else:
                cls.debug(113, token=token)
                return False
        else:
            cls.debug(113, token=token)
            return False

    @classmethod
    def signup(cls, token, user, *args, **kwargs):
        """Create account in trello"""
        from kb.apps.models import App
        from accounts.models import AppAccount
        unpacked = unpack_token(token)
        if not user.email:
            cls.debug(411, user=user, info='No user email')
            return False

        if not user.first_name and not user.last_name:
            cls.debug(411, user=user, info='No first or last name known.')

        try:
            dsc_token = cls.get_regex_match_from_url(
                token, cls.SIGNUP_PAGE, r'.*window.dsc="([^"]+)";.*').group(1)
        except AttributeError:
            cls.debug(510, field="window.dsc")
            cls.debug(411, user=user)
            return False

        credentials = AppAccount.generate(
            app=App.objects.get(pk=unpacked['app']),
            user=user)
        credentials.username = user.email

        payload = {
            "fullName": user.profile.full_name,
            "email": user.email,
            "locale": "nl",
            "password": credentials.password,
            "source": "web",
            "dsc": dsc_token
        }
        response = cls.form_post(
            token=token,
            url=cls.SIGNUP_URL,
            payload=payload,
            custom_headers={
                'Referer': cls.SIGNUP_PAGE})

        if response.status_code == 200:
            credentials.save()
            cls.debug(111, user=user)
            return True
        else:
            cls.debug(411, user=user)
            secret_body_values = (credentials.username, credentials.password)
            cls.debug_http_package(response.request, label='Signup request',
                                   secret_body_values=secret_body_values)
            cls.debug_http_package(response, label='Signup response')
            return False


    @classmethod
    def register_signals(cls):
        """Register signals needed for the trello.com connector"""
        pass
