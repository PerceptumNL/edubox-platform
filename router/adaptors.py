from bs4 import BeautifulSoup

import json
import requests
import binascii

from router import utils
from .models import ServerCredentials
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
    def signup(cls, token, *args, **kwargs):
        raise NotImplementedError()

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
        response = requests.get(cls.base16_encode(url), params={'token':token})
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
            "params": {'token': token}
            "allow_redirects":False,
            "headers": headers,
            "url": cls.base16_encode(url)
        }
        if "application/json" in headers['Content-Type']:
            params['json'] = payload
        else:
            params['data'] = payload
        return requests.post(**params)

    @classmethod
    def base16_encode(cls, url):
        return binascii.b2a_hex(bytes(netloc, "utf-8")).decode("utf-8")+
            ".codecult.nl"


class CodeOrgAdaptor(BaseAdaptor):
    LOGIN_CHECK_URL = "https://studio.code.org/users/edit"
    LOGIN_PAGE_URL = "https://studio.code.org/users/sign_in"
    LOGIN_URL = "https://studio.code.org/users/sign_in"
    SECTION_LOGIN_PAGE_URL = "https://studio.code.org/sections/%s"
    SECTION_LOGIN_URL = "https://studio.code.org/sections/%s/log_in"
    SECTION_INDEX = "https://code.org/v2/sections"
    SECTION_STUDENTS_URL = "https://code.org/v2/sections/%d/students"
    TEACHER_DASHBOARD_PAGE = "https://code.org/teacher-dashboard"
    APP_SCRIPT_URL = "adaptor/code_org.js"

    @classmethod
    def is_logged_in(cls, token, *args, **kwargs):
        response = requests.head(cls.base16_encode(cls.LOGIN_CHECK_URL),
            params={'token': token},
            allow_redirects=False)
        return response.status_code == 302

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
                "utf8": "\u2713",
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
                "utf8": "\u2713",
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
    def teacher_login(cls, token, user, app):
        try:
            credentials = ServerCredentials.objects.get(app=app, user=user)
        except ServerCredentials.DoesNotExist:
            if cls.teacher_signup(cls, teacher_token):
                credentials = ServerCredentials.objects.get(app=user, user=user)
            else:
                return False

        return cls.login(credentials, token)
    
    #TODO: Should sign the teacher up using his email account
    @classmethod
    def teacher_signup(cls, token):
        pass

    @classmethod
    def signup(cls, token, *args, **kwargs):
        unpacked = unpack_token(token)
        user = User.objects.get(pk=unpacked['user'])
        if user.profile.is_teacher():
            cls.teacher_login(token, unpacked['user'], unpacked['app'])
        else:
            #Get the first teacher of this users group
            group = Group.objects.get(pk=unpacked['group'])
            role = Role.objects.get(role='Teacher')
            teacher = Membership.objects.filter(group=group, role=role).first().user
            teacher_token = create_token(user=teacher.pk, group=unpacked['group'], 
                app=unpacked['app'])
            
            if not cls.teacher_login(teacher_token, teacher.pk, unpacked['app']):
                cls.debug("Cannot login as group teacher.")
                return False
            # Check if section is created for institute, else create it
            sections = requests.get(cls.base16_encode(cls.SECTION_INDEX)
                params={'token': teacher_token}).json()
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
                        cls.base16_encode(section_response.headers['location']),
                        params={'token': teacher_token}
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
                token=teacher_token
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
