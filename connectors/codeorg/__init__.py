"""Module containing connector class for Code.org"""
import requests

from connectors import BaseConnector
from kb.helpers import create_token, unpack_token

class Connector(BaseConnector):
    """Connector class for Code.org"""
    LOG_NAME = __name__
    HOME_PAGE = "https://studio.code.org"
    USER_LANGUAGE = HOME_PAGE+"/locale"
    USERS_URL = HOME_PAGE+"/users"
    LOGIN_CHECK_URL = USERS_URL+"/edit"
    LOGIN_PAGE_URL = USERS_URL+"/sign_in"
    LOGIN_URL = LOGIN_PAGE_URL
    SECTION_LOGIN_PAGE_URL = HOME_PAGE+"/sections/%s"
    SECTION_LOGIN_URL = HOME_PAGE+"/sections/%s/log_in"
    SECTION_INDEX = "https://code.org/v2/sections"
    SECTION_STUDENTS_URL = "https://code.org/v2/sections/%d/students"
    TEACHER_DASHBOARD_PAGE = "https://code.org/teacher-dashboard"
    TEACHER_SIGNUP_PAGE = USERS_URL + "/sign_up?user%5Buser_type%5D=teacher"
    TEACHER_SIGNUP = USERS_URL

    @classmethod
    def is_logged_in(cls, token, *args, **kwargs):
        """Returns True if user is still logged in."""
        response = requests.head(cls.route_url(cls.LOGIN_CHECK_URL),
                                 params={'token': token},
                                 allow_redirects=False)
        if response.status_code != 302:
            cls.debug(114, token=token)
            return True
        else:
            return False

    @classmethod
    def _login_normal(cls, token, credentials):
        """Login user into code.org via normal login mode."""
        try:
            authenticity_token = cls.get_field_value_from_url(
                token, cls.LOGIN_PAGE_URL, "authenticity_token")
        except (KeyError, TypeError):
            cls.debug(510, field="authenticity_token")
            return None

        payload = {
            "user[login]": credentials.username,
            "user[password]": credentials.password,
            "utf8": u"\u2713",
            "authenticity_token": authenticity_token,
            "user[remember_me]": "1",
            "user[hashed_email]": "",
            "commit": "Sign in"
        }
        return cls.form_post(token, cls.LOGIN_URL, payload)

    @classmethod
    def _login_class(cls, token, credentials, section):
        """Login user into code.org via class-based login mode."""
        login_page_url = cls.SECTION_LOGIN_PAGE_URL % (section,)
        try:
            authenticity_token = cls.get_field_value_from_url(
                token, login_page_url, "authenticity_token")
        except (KeyError, TypeError):
            cls.debug(510, field="authenticity_token")
            return None

        payload = {
            "user_id": credentials.username,
            "secret_words": credentials.password,
            "utf8": u"\u2713",
            "authenticity_token": authenticity_token,
            "secret_picture_id": "",
            "button": ""
        }
        return cls.form_post(
            token=token,
            url=cls.SECTION_LOGIN_URL % (section,),
            payload=payload,
            custom_headers={
                'Referer': cls.SECTION_LOGIN_PAGE_URL % (section,)})

    @classmethod
    def login(cls, token, credentials, *args, **kwargs):
        from accounts.models import AppAccount
        if not isinstance(credentials, AppAccount):
            cls.debug(512)
            cls.debug(113, token=token)
            return False
        secret_body_values = [credentials.username, credentials.password]
        params = credentials.parameters or {"login_mode": "normal"}
        cls.debug(110, params=params)
        if params['login_mode'] == "normal":
            login_response = cls._login_normal(token, credentials)
        elif params['login_mode'] == "class":
            if 'section' not in params:
                cls.debug(511, param="section", value='None')
                cls.debug(113, token=token)
                return False
            login_response = cls._login_class(
                token, credentials, params['section'])
        else:
            cls.debug(511, param="login_mode", value=params.get('login_mode'))
            cls.debug(113, token=token)
            return False

        if login_response is None:
            cls.debug(113, token=token)
            return False

        cls.debug_http_package(login_response.request, label='Login request',
                               secret_body_values=secret_body_values)
        cls.debug_http_package(login_response, label='Login response')

        if login_response.status_code == 302:
            cls.debug(112, token=token)
            return True
        else:
            cls.debug(113, token=token)
            return False

    @classmethod
    def signup_teacher(cls, token, user):
        """Create teacher account in code.org"""
        from kb.apps.models import App
        from accounts.models import AppAccount
        unpacked = unpack_token(token)
        if not user.email:
            cls.debug(411, user=user, info='No user email')
            return False

        try:
            authenticity_token = cls.get_field_value_from_url(
                token, cls.TEACHER_SIGNUP_PAGE, "authenticity_token")
        except (KeyError, TypeError):
            cls.debug(510, field="authenticity_token")
            cls.debug(411, user=user)
            return False

        credentials = AppAccount.generate(
            app=App.objects.get(pk=unpacked['app']),
            user=user)
        credentials.username = user.email
        from hashlib import md5
        hashed_email = md5(
            user.email.encode("ascii", 'ignore').lower()).hexdigest()

        payload = {
            "utf8": u"\u2713",
            "authenticity_token": authenticity_token,
            "user[user_type]": "teacher",
            "user[locale]": "nl-nl",
            "user[hashed_email]": hashed_email,
            "user[name]": user.profile.full_name,
            "user[email]": user.email,
            "user[password]": credentials.password,
            "user[password_confirmation]": credentials.password,
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
                'Referer': cls.TEACHER_SIGNUP_PAGE})

        if response.is_redirect:
            credentials.save()
            # Ensure the language is set to Dutch
            try:
                authenticity_token = cls.get_field_value_from_url(
                    token, cls.HOME_PAGE, "authenticity_token")
            except (KeyError, TypeError):
                cls.debug(510, field="authenticity_token")
                cls.debug(411, user=user)
                return False

            response = cls.form_post(
                token=token,
                url=cls.USER_LANGUAGE,
                payload={
                    'utf8': u'\u2713',
                    'locale': 'nl-nl',
                    'authenticity_token': authenticity_token,
                    'return_to': cls.HOME_PAGE},
                custom_headers={
                    'Referer': cls.HOME_PAGE
                })
            if not response.is_redirect:
                cls.debug(412, lang="nl-nl", user=user)

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
    def signup_student(cls, token, user):
        """Create student account on code.org"""
        from kb.groups.models import Group, Membership, Role
        from kb.apps.models import App
        from accounts.models import AppAccount
        unpacked = unpack_token(token)
        #Get the first teacher of this users group
        group = Group.objects.get(pk=unpacked['group'])
        role = Role.objects.get(role='Teacher')
        teacher = Membership.objects.exclude(
            user__user__email="").filter(
                group=group, role=role).first().user.user
        teacher_token = create_token(
            user=teacher.pk,
            group=unpacked['group'],
            app=unpacked['app'])
        if not cls.is_logged_in(teacher_token):
            credentials = cls.get_or_create_credentials(
                teacher_token, teacher, unpacked['app'])
            if credentials is None:
                cls.debug(411, user=user,
                          info='No credentials for teacher %d' % (teacher.pk,))
                return False
            elif not cls.login(teacher_token, credentials):
                cls.debug(411, user=user,
                          info='Cannot login teacher %d' % (teacher.pk,))
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
                cls.debug(411, user=user, info='Cannot create section')
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
            from json import dumps
            account = response.json()[0]
            credentials = AppAccount.objects.create(
                user=user,
                app=App.objects.get(pk=unpacked['app']),
                username=account['id'],
                password=account['secret_words'],
                params=dumps({
                    'login_mode': 'class',
                    'section': section_code,
                    'username': account['username']}))

            # Login to set language
            if not cls.login(token, credentials):
                cls.debug(410, token=token)
                cls.debug(411, user=user)
                return False

            # Ensure the language is set to Dutch
            try:
                authenticity_token = cls.get_field_value_from_url(
                    token, cls.HOME_PAGE, "authenticity_token")
            except (KeyError, TypeError):
                cls.debug(510, field="authenticity_token")
                cls.debug(411, user=user)
                return False

            response = cls.form_post(
                token=token,
                url=cls.USER_LANGUAGE,
                payload={
                    'utf8': u'\u2713',
                    'locale': 'nl-nl',
                    'authenticity_token': authenticity_token,
                    'return_to': cls.HOME_PAGE},
                custom_headers={
                    'Referer': cls.HOME_PAGE
                })

            if not response.is_redirect:
                cls.debug(412, lang="nl-nl", user=user)

            cls.debug(111, user=user)
            return True
        else:
            secret_body_values = (credentials.username, credentials.password)
            cls.debug(411, user=user, info="Signup request returned %d" % (
                response.status_code,))
            cls.debug_http_package(response.request, label='Signup request',
                                   secret_body_values=secret_body_values)
            cls.debug_http_package(response, label='Signup response')
            return False

    @classmethod
    def signup(cls, token, user, *args, **kwargs):
        """Create account for user in code.org"""
        if user.profile.is_teacher():
            return cls.signup_teacher(token, user, *args, **kwargs)
        else:
            return cls.signup_student(token, user, *args, **kwargs)

    @classmethod
    def register_signals(cls):
        """Register signals needed for the code.org connector"""
        from kb.events.models import SubmittedEvent
        from django.db.models.signals import post_save
        from .signals import handle_codeorg_submission
        post_save.connect(handle_codeorg_submission, sender=SubmittedEvent)
        cls.debug(201)
