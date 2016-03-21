import requests
from connectors import BaseConnector
from kb.helpers import create_token, unpack_token

class Connector(BaseConnector):
    LOG_NAME = __name__
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

        csrf_response = requests.head(
            cls.route_url(cls.CSRF_TOKEN_PAGE),
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
            custom_headers={
                'Referer': cls.HOME_PAGE,
                'X-CSRFToken': csrf_token,
                'Content-Type': 'application/json;charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            })

        cls.debug_http_package(login_response.request, label='Login request',
                               secret_body_values=secret_body_values)
        cls.debug_http_package(login_response, label='Login response')

        if cls.is_logged_in(token):
            cls.debug(112, token=token)
            return True
        else:
            cls.debug(113, token=token)
            return False

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
                user=user, invalid_usernames=invalid_usernames)
            check_username_response = requests.get(
                cls.route_url(cls.CHECK_USERNAME)+credentials.username+"/")
            if check_username_response.json()[0]['msg'] == "valid username":
                username_valid = True
            else:
                invalid_usernames.append(credentials.username)

        secret_body_values = [credentials.username, credentials.password]

        csrf_response = requests.head(
            cls.route_url(cls.CSRF_TOKEN_PAGE),
            params={'token': token, 'cpeek': 'scratchcsrftoken'})
        if 'X-Cookie-Peek' not in csrf_response.headers:
            cls.debug(411, user=user, info="Missing CSRF Cookie Peek")
            return False
        else:
            csrf_token = csrf_response.headers['X-Cookie-Peek']

        payload = {
            "username": credentials.username,
            "password": credentials.password,
            "birth_month": user.profile.date_of_birth.month,
            "birth_year": user.profile.date_of_birth.year,
            "gender": ("male" if user.profile.gender == 1 else "female"),
            "country": settings.SCRATCH_SIGNUP_COUNTRY,
            "email": settings.SCRATCH_SIGNUP_EMAIL,
            "is_robot": False,
            "should_generate_admin_ticket": False,
            "usernames_and_messages": (
                "<table class='banhistory'>\n",
                "\t<thead>\n",
                "\t\t<tr>\n",
                "\t\t\t<td>Account</td>\n",
                "\t\t\t<td>Email</td>\n",
                "\t\t\t<td>Reason</td>\n"
                "\t\t\t<td>Date</td>\n"
                "\t\t</tr>\n"
                "\t</thead>\n"
                "</table>\n"),
            "csrfmiddlewaretoken": csrf_token,
        }

        signup_response = cls.form_post(
            token,
            cls.SIGNUP_URL,
            payload,
            custom_headers={
                'Referer': cls.SIGNUP_PAGE,
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest'
            })

        signup_body = signup_response.json()
        if signup_body[0]['success'] and signup_body[0]['logged_in']:
            credentials.save()
            cls.debug(111, user=user)
            return True
        else:
            cls.debug_http_package(signup_response.request,
                                   label='Signup request',
                                   secret_body_values=secret_body_values)
            cls.debug_http_package(signup_response, label='Signup response')
            cls.debug(101, info=signup_response.text)
            cls.debug(411, user=user,
                      info="Scratch says "+signup_body[0]['msg'])
            return False

    @classmethod
    def register_signals(cls):
        pass
