from connectors import BaseConnector
from kb.helpers import create_token, unpack_token
import requests

class Connector(BaseConnector):
    HOME_PAGE = "https://scratch.mit.edu/"
    CSRF_TOKEN_PAGE = HOME_PAGE+"csrf_token/"
    USERS_URL = HOME_PAGE+"accounts/"
    LOGIN_CHECK_URL = USERS_URL+"settings/"
    LOGIN_URL = USERS_URL+"login/"
    SIGNUP_URL = USERS_URL+"register_new_user/"
    SIGNUP_PAGE = USERS_URL+"standalone-registration/"
    CHECK_USERNAME = USERS_URL+"check_username/"

    @classmethod
    def is_logged_in(cls, token, *args, **kwargs):
        response = requests.head(cls.route_url(cls.LOGIN_CHECK_URL),
            params={'token': token},
            allow_redirects=False)
        return response.status_code != 302

    @classmethod
    def login(cls, token, credentials, *args, **kwargs):
        if credentials is None:
            return False
        secret_body_values = [credentials.username, credentials.password]

        csrf_response = requests.head(cls.route_url(cls.CSRF_TOKEN_PAGE),
            params={'token': token, 'cpeek': 'scratchcsrftoken'})
        if 'X-Cookie-Peek' not in csrf_response.headers:
            cls.debug("Missing CSRF Cookie Peek")
            return False
        else:
            csrf_token = csrf_response.headers['X-Cookie-Peek']

        payload = {
            "username": credentials.username,
            "password": credentials.password,
            "csrftoken": csrf_token,
            "useMessages": True
        }

        login_response = cls.form_post(
            token,
            cls.LOGIN_URL,
            payload,
            custom_headers = {
                'Referer': cls.HOME_PAGE,
                'X-CSRFToken': csrf_token,
                'Content-Type': 'application/json;charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            })

        cls.debug_http_package(login_response.request, label='Login request',
                secret_body_values=secret_body_values)
        cls.debug_http_package(login_response, label='Login response')

        return cls.is_logged_in(token)

    @classmethod
    def signup(cls, token, user, *args, **kwargs):
        from kb.apps.models import App
        from accounts.models import AppAccount
        from django.conf import settings
        unpacked = unpack_token(token)

        username_valid = False
        invalid_usernames = []
        credentials = None
        while not username_valid:
            credentials = AppAccount.generate(
                app=App.objects.get(pk=unpacked['app']),
                user=user,
                invalid_usernames=invalid_usernames)
            check_username_response = requests.get(
                cls.route_url(cls.CHECK_USERNAME)+credentials.username+"/")
            if check_username_response.json()[0].msg == "valid username":
                username_valid = True
            else:
                invalid_usernames.append(credentials.username)

        secret_body_values = [credentials.username, credentials.password]

        csrf_response = requests.head(cls.route_url(cls.CSRF_TOKEN_PAGE),
            params={'token': token, 'cpeek': 'scratchcsrftoken'})
        if 'X-Cookie-Peek' not in csrf_response.headers:
            cls.debug("Missing CSRF Cookie Peek")
            return False
        else:
            csrf_token = csrf_response.headers['X-Cookie-Peek']

        payload = {
            "username": credentials.username,
            "password": credentials.password,
            "csrftoken": csrf_token,
            "birth_month": user.profile.date_of_birth.month,
            "birth_year": user.profile.date_of_birth.year,
            "gender": ("male" if user.profile.gender == 1 else "female"),
            "country": settings.SCRATCH_SIGNUP_COUNTRY,
            "email": settings.SCRATCH_SIGNUP_EMAIL,
            "is_robot": False,
            "should_generate_admin_ticket": False
        }

        login_response = cls.form_post(
            token,
            cls.SIGNUP_URL,
            payload,
            custom_headers = {
                'Referer': cls.SIGNUP_PAGE,
                'X-CSRFToken': csrf_token,
                'Content-Type': 'application/json;charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            })

        cls.debug_http_package(login_response.request, label='Login request',
                secret_body_values=secret_body_values)
        cls.debug_http_package(login_response, label='Login response')

    @classmethod
    def register_signals(cls):
        pass
