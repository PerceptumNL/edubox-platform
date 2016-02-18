from bs4 import BeautifulSoup

import json

from router import utils
from .models import ServerCredentials

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
    def create_session(cls):
        from requests import Session
        return Session()

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
        if "application/json" in headers['Content-Type']:
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
    SECTION_INDEX = "https://code.org/v2/sections"
    SECTION_STUDENTS_URL = "https://code.org/v2/sections/%d/students"
    TEACHER_DASHBOARD_PAGE = "https://code.org/teacher-dashboard"


    @classmethod
    def is_logged_in(cls, user, session, *args, **kwargs):
        response = session.request(method="HEAD",
                                   url=cls.LOGIN_CHECK_URL,
                                   allow_redirects=False)
        return response.status_code == 302

    @classmethod
    def login(cls, credentials, user, session, *args, **kwargs):
        if credentials is None:
            return False
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
    def login_as_default_teacher(cls, session, app):
        from django.conf import settings
        if settings.DEFAULT_CODE_ORG_TEACHER is None:
            return False
        else:
            from django.contrib.auth import get_user_model
            try:
                teacher = get_user_model().objects.get(
                    pk=settings.DEFAULT_CODE_ORG_TEACHER)
            except get_user_model().DoesNotExist:
                return False

        try:
            credentials = ServerCredentials.objects.get(
                app=app, user=teacher)
        except ServerCredentials.DoesNotExist:
            cls.debug("Teacher credentials not found for this app.")
            return False

        return cls.login(credentials, teacher, session)

    @classmethod
    def signup(cls, user, session, app, *args, **kwargs):
        if user.profile.is_teacher():
            pass
        else:
            teacher_session = cls.create_session()
            # Login as generic teacher
            if not cls.login_as_default_teacher(teacher_session, app):
                cls.debug("Cannot login as default teacher.")
                return False
            # Check if section is created for institute, else create it
            sections = teacher_session.request(
                url=cls.SECTION_INDEX, method="GET").json()
            for section in sections:
                if section['name'] == user.profile.institute.email_domain:
                    break
            else:
                # Create section
                payload = {
                    "editing": True,
                    "login_type": "word",
                    "name": user.profile.institute.email_domain,
                    "grade":"Other"
                }

                section_response = cls.form_post(
                    session=teacher_session,
                    url=cls.SECTION_INDEX,
                    payload=payload,
                    custom_headers={
                        'Referer': cls.TEACHER_DASHBOARD_PAGE,
                        'Content-Type': 'application/json;charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest'
                    })
                if not section_response.is_redirect:
                    return False
                else:
                    section = teacher_session.request(
                        method='GET',
                        url=section_response.headers['location'],
                        custom_headers={
                            'Referer': cls.TEACHER_DASHBOARD_PAGE,
                            'Content-Type': 'application/json;charset=UTF-8',
                            'X-Requested-With': 'XMLHttpRequest'
                        }).json()

            section_code = section['code']
            section_id = section['id']
            # Add student
            payload = [{ "editing": True, "name": user.profile.full_name }]
            response = cls.form_post(
                session=teacher_session,
                url=cls.SECTION_STUDENTS_URL % (section_id,),
                payload=payload,
                custom_headers={
                    'Referer': cls.TEACHER_DASHBOARD_PAGE,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest'
                })
            if response.status_code == 200:
                account = response.json()[0]
                ServerCredentials.objects.create(
                    user=user,
                    app=app,
                    username=account['id'],
                    password=account['secret_words'],
                    params=json.dumps({
                        'login_mode': 'class',
                        'section': section_code,
                        'username': account['username']}))
                cls.debug("Created account for %d in code.org" % (user.pk,))
                return True
            else:
                return False
