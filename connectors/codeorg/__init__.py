from connectors import BaseConnector
from kb.helpers import create_token, unpack_token
import requests

class Connector(BaseConnector):
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
        from kb.apps.models import App
        from accounts.models import AppAccount
        unpacked = unpack_token(token)
        if user.profile.is_teacher():
            if not user.email:
                return False
            login_document = cls.fetch_and_parse_document(
                token, cls.TEACHER_SIGNUP_PAGE)
            authenticity_token = cls.get_field_value_from_document(
                login_document, "authenticity_token")

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
                    'Referer': cls.TEACHER_SIGNUP_PAGE
                })
            if response.is_redirect:
                credentials.save()
                # Ensure the language is set to Dutch
                language_document = cls.fetch_and_parse_document(
                    token, cls.HOME_PAGE)
                authenticity_token = cls.get_field_value_from_document(
                    language_document, "authenticity_token")
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
                    cls.debug("Could not set language to nl-nl")
                return True
            else:
                return False
        else:
            from kb.groups.models import Group, Membership, Role
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
            credentials = cls.get_or_create_credentials(
                teacher_token, teacher, unpacked['app'])
            if credentials is None:
                cls.debug("Cannot find or create credentials for %s in %s" % (
                    teacher, str(unpacked['app'])))
                return False
            if not cls.is_logged_in(teacher_token):
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
                    cls.debug('Could not login student with credentials.')
                    return False

                # Ensure the language is set to Dutch
                language_document = cls.fetch_and_parse_document(
                    token, cls.HOME_PAGE)
                authenticity_token = cls.get_field_value_from_document(
                    language_document, "authenticity_token")
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
                    cls.debug("Could not set language to nl-nl")
                cls.debug("Created account for %d in code.org" % (user.pk,))
                return True
            else:
                return False

    @classmethod
    def register_signals(cls):
        from kb.events.models import SubmittedEvent
        from django.db.models.signals import post_save
        from .signals import handle_codeorg_submission
        post_save.connect(handle_codeorg_submission, sender=SubmittedEvent)
