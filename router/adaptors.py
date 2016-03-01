from bs4 import BeautifulSoup

import json
import requests
import binascii

from router import utils
from .models import ServerCredentials
from kb.apps.models import App
from kb.helpers import create_token, unpack_token
from kb.groups.models import Group, Membership, Role

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
        try:
            credentials = ServerCredentials.objects.get(
                app__pk=app_pk, user=user)
        except ServerCredentials.DoesNotExist:
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
        urlparts = urlsplit(url)
        return urlunsplit((
            urlparts.scheme,
            "%s.codecult.nl" % ( binascii.b2a_hex(
                bytes(urlparts.netloc, "utf-8")).decode("utf-8")),
            urlparts.path,
            urlparts.query,
            urlparts.fragment))


class CodeOrgAdaptor(BaseAdaptor):
    USERS_URL = "https://studio.code.org/users"
    LOGIN_CHECK_URL = USERS_URL+"/edit"
    LOGIN_PAGE_URL = USERS_URL+"/sign_in"
    LOGIN_URL = LOGIN_PAGE_URL
    SECTION_LOGIN_PAGE_URL = "https://studio.code.org/sections/%s"
    SECTION_LOGIN_URL = "https://studio.code.org/sections/%s/log_in"
    SECTION_INDEX = "https://code.org/v2/sections"
    SECTION_STUDENTS_URL = "https://code.org/v2/sections/%d/students"
    TEACHER_DASHBOARD_PAGE = "https://code.org/teacher-dashboard"
    TEACHER_SIGNUP_PAGE = USERS_URL + "/sign_up?user%5Buser_type%5D=teacher"
    TEACHER_SIGNUP = USERS_URL
    APP_SCRIPT_URL = "adaptor/code_org.js"

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
        params = credentials.parameters or {"login_mode": "normal"}
        if params['login_mode'] == "normal":
            cls.debug('Login mode: normal')
            login_document = cls.fetch_and_parse_document(
                token, cls.LOGIN_PAGE_URL)
            authenticity_token = cls.get_field_value_from_document(
                login_document, "authenticity_token")
            payload = {
                "user[login]": credentials.username,
                "user[password]": credentials.password,
                "utf8": u"\u2713",
                "authenticity_token": authenticity_token,
                "user[remember_me]": "1",
                "user[hashed_email]": "",
                "commit": "Sign in"
            }
            login_response = cls.form_post(token, cls.LOGIN_URL, payload)
        elif params['login_mode'] == "class":
            cls.debug('Login mode: class')
            if 'section' not in params:
                return False
            login_document = cls.fetch_and_parse_document(
                token, cls.SECTION_LOGIN_PAGE_URL % (params['section'],))
            authenticity_token = cls.get_field_value_from_document(
                login_document, "authenticity_token")
            payload = {
                "user_id": credentials.username,
                "secret_words": credentials.password,
                "utf8": u"\u2713",
                "authenticity_token": authenticity_token,
                "secret_picture_id": "",
                "button": ""
            }
            login_response = cls.form_post(
                token=token,
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
    def signup(cls, token, user, *args, **kwargs):
        unpacked = unpack_token(token)
        if user.profile.is_teacher():
            if not user.email:
                return False
            login_document = cls.fetch_and_parse_document(
                token, cls.TEACHER_SIGNUP_PAGE)
            authenticity_token = cls.get_field_value_from_document(
                login_document, "authenticity_token")

            from strgen import StringGenerator
            password = StringGenerator("[\w\d]{20}").render()
            from hashlib import md5
            hashed_email = md5(user.email).hexdigest()

            payload = {
                "utf8": u"\u2713",
                "authenticity_token": authenticity_token,
                "user[type]": "teacher",
                "user[locale]": "nl-nl",
                "user[hashed_email]": hashed_email,
                "user[name]": user.profile.full_name,
                "user[email]": user.email,
                "user[password]": password,
                "user[password_confirmation]": password,
                "user[school]": user.profile.institute.title,
                "user[full_address]": "",
                "user[age]": 21,
                "commit": "Sign up"
            }
            response = cls.form_post(
                token=token,
                url=cls.TEACHER_SIGNUP,
                payload=payload,
                custom_headers={
                    'Referer': cls.TEACHER_SIGNUP_PAGE
                })
            return response.is_redirect
        else:
            #Get the first teacher of this users group
            group = Group.objects.get(pk=unpacked['group'])
            role = Role.objects.get(role='Teacher')
            teacher = Membership.objects.filter(
                group=group, role=role).first().user.user
            teacher_token = create_token(
                user=teacher.pk,
                group=unpacked['group'],
                app=unpacked['app'])
            if not cls.is_logged_in(teacher_token):
                credentials = cls.get_or_create_credentials(
                    teacher_token, teacher, unpacked['app'])
                if credentials is None:
                    cls.debug("Cannot find or create credentials for %s in %s" % (
                        teacher, str(unpacked['app'])))
                    return False

                if not cls.login(teacher_token, credentials):
                    cls.debug("Cannot login as group teacher.")
                    return False
            # Check if section is created for institute, else create it
            sections = requests.get(cls.route_url(cls.SECTION_INDEX),
                params={'token': teacher_token}).json()
            user_section_name = "%s (%s)" % (
                group.title, user.profile.institute.email_domain)
            for section in sections:
                if section['name'] == user_section_name:
                    break
            else:
                # Create section
                payload = {
                    "editing": True,
                    "login_type": "word",
                    "name": user_section_name,
                    "grade":"Other"
                }

                section_response = cls.form_post(
                    token=teacher_token,
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
                    section = requests.get(
                        section_response.headers['location'],
                        headers={
                            'Referer': cls.TEACHER_DASHBOARD_PAGE,
                            'Content-Type': 'application/json;charset=UTF-8',
                            'X-Requested-With': 'XMLHttpRequest'
                        }).json()

            section_code = section['code']
            section_id = section['id']
            # Add student
            age = cls.determine_age(user)
            if age is not None:
                payload = [{
                    "editing": True,
                    "name": user.profile.full_name,
                    "age": '21+' if age > 20 else str(age)
                }]
            else:
                payload = [{
                    "editing": True,
                    "name": user.profile.full_name,
                }]
            response = cls.form_post(
                token=teacher_token,
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
                    app=App.objects.get(pk=unpacked['app']),
                    username=account['id'],
                    password=account['secret_words'],
                    params=json.dumps({
                        'login_mode': 'class',
                        'section': section_code,
                        'username': account['username']}))
                # TODO: Set language to NL
                cls.debug("Created account for %d in code.org" % (user.pk,))
                return True
            else:
                return False

    @classmethod
    def get_app_script(cls, *args, **kwargs):
        from django.conf import settings
        return "https://backend.codecult.nl%s%s" % (
            settings.STATIC_URL, cls.APP_SCRIPT_URL)
