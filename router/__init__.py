"""
Routing local requests to remote servers

Remote routing is delegated to an instance of :py:class:`Router` or any of its
subclassed. Which Router class will be used is determined by
:py:meth:`loader.middleware.SubdomainAppRoutingMiddleware`, for which the
routing dict is provided by :py:meth:`Router.get_subdomain_routing_mapping`.

The delegation flow is as follows:

1. An incoming request is matched to the subdomain patterns, resulting in a
   Router (sub)class.
2. :py:meth:`Router.route_path_by_subdomain` is called with the request object
   and strings matched in the subdomain pattern's groups, which creates an
   instance of `Router`.
3. :py:meth:`Router.route_request` of the router instance is called with the request
   object, triggering the actual routing which will eventually return a
   :py:class:`django.http.HttpResponse` object to be send to the client.

The internal routing flow is as follows:

1. :py:meth:`Router.route_request`
2. :py:meth:`Router.get_remote_response`
3. :py:meth:`Router.get_response`
    a. :py:meth:`Router.get_resonse_content`
    b. :py:meth:`Router.alter_response_content`
    c. :py:meth:`Router.get_response_body`

The vocabulary used in this module:

routed domain
    A domain string that, when resolved, would be handled by a router
    communicating with the remote domain it is associated with.

routed URL
    Like a routed domain, but potentially including a path, query and fragment.

routing, rerouting of an URL
    Changing the URL to a routed url

unrouting
    Changing a routed url back to the (original) remote url.

request / response
    The :py:meth:`django.http.HttpRequest` and
    :py:meth:`django.http.HttpResponse` objects belonging to the communication
    between the client (i.e. the browser) and the router.

remote request / remote response
    The :py:meth:`requests.Request` and :py:meth:`requests.Response` objects
    belonging to the communication between the router and the remote server the
    request is routed to.
"""
import re
import pickle
import requests
import subdomains
from base64 import b32encode, b32decode
from binascii import Error as BinASCIIError
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit, quote, unquote

from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.clickjacking import xframe_options_exempt

from router import utils

class BaseRouter():
    """
    Generic base class for all router classes.

    :param str remote_domain: The hostname of the remote sever.
    """

    request = None
    """Incoming request object to be routed."""
    remote_domain = None
    """The remote domain the request must be routed to."""
    remote_session = None
    """The :py:class:`requests.Session` object used for all remote requests."""

    def __init__(self, remote_domain):
        self.remote_domain = remote_domain
        self.remote_session = requests.Session()

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

    @staticmethod
    def pack_secure_params(params, sep='|'):
        plain = sep.join([str(param) for param in params])
        pad = (-len(plain) % 16) * '*'
        plain += pad

        #Use the django settings secret key to encrypt with AES
        key = settings.SECRET_KEY[:16]
        crypt = AES.new(key, AES.MODE_ECB)
        cipher = crypt.encrypt(plain)

        #Encode in base64
        token = b32encode(cipher).decode('utf-8').replace("=","-")
        return token

    @staticmethod
    def unpack_secure_token(token, sep='|'):
        #Decode from base64
        token = b32decode(token.replace("-","="), casefold=True)

        #Decrypt AES using settings secret key
        key = settings.SECRET_KEY[:16]
        cipher = AES.new(key, AES.MODE_ECB)
        context = cipher.decrypt(token)

        #Seperate the elements from the string
        context = context.decode('utf-8')
        params = context.rstrip('*').split(sep)
        return params

    @classmethod
    @xframe_options_exempt
    def route_path_by_subdomain(cls, request, domain_hash):
        try:
            domain, = cls.unpack_secure_token(domain_hash)
        except ValueError:
            cls.debug("Router could not unpack domain token")
            raise Http404()

        cls.debug("Router matched domain %s" % (domain,))
        router = cls(domain)
        return router.route_request(request)

    @classmethod
    def get_subdomain_patterns(cls):
        """
        Return a tuple of subdomain pattern strings that should be handled by
        this router class.

        :rtype: tuple of regex strings
        """
        raise NotImplementedError()

    @classmethod
    def get_subdomain_routing_mapping(cls, map_to_function=True):
        """
        Return a dictionary mapping subdomain patterns to router classes.

        :param bool map_to_function: Map subdomains to routing functions rather
            than classes.
        :return: a dictionary mapping pattern strings to either classes or
            functions
        """
        mapping = {}
        # Add subdomain patterns of this class
        for pattern in cls.get_subdomain_patterns():
            if map_to_function:
                mapping[pattern] = cls.route_path_by_subdomain
            else:
                mapping[pattern] = cls

        # Add subdomain patterns of subclasses
        for subclass in cls.__subclasses__():
            mapping.update(subclass.get_subdomain_routing_mapping(
                map_to_function))
        return mapping

    def get_routed_url(self, url, path_only=True):
        """
        Translate the url to a routed version.

        :param str url: a fully qualified URL or a part of it.
        :param bool path_only: whether to return only the path string or the
            complete url.
        :return: routed url or path depending on `path_only`
        """
        parts = urlsplit(url)
        if path_only:
            return parts.path
        else:
            return urlunsplit((
                parts.scheme or self.request.scheme,
                self.get_routed_domain(url),
                parts.path,
                parts.query,
                parts.fragment))

    def get_routed_domain(self, url):
        """
        Return a routed version of the domain in ``url``.

        :param str url: The url that contains the domain that will be routed
        :return: a routed domain string
        """
        parts = urlsplit(url)
        netloc = parts.netloc or self.remote_domain
        return "%s-rtr.%s" % (
            self.pack_secure_params((netloc,)), subdomains.utils.get_domain())

    def get_unrouted_domain_by_match(self, **kwargs):
        """
        Return the original domain extracted from the routed url pattern match.
        The arguments to this function are formed by the matched groups in the
        pattern.

        If `domain` is not  one of the matched fields, the current domain is
        returned as provided by :py:func:`subdomains.utils.get_domain`.

        :param kwargs: keyword argument list containing the matched regex
                       groups.
        :return: the unrouted domain string or the current domain.
        """
        domain_hash = kwargs.get('domain_hash', None)
        if domain_hash is None:
            return subdomains.utils.get_domain()
        else:
            return self.unpack_secure_token(domain_hash)[0]

    def get_unrouted_url(self, routed_url, path_only=True):
        """
        Translate a routed url back to the original version.

        :param str url: a routed fully qualified URL or a part of it.
        :param bool path_only: whether to return only the path string or the
            complete url.
        :return: the unrouted url or path depending on `path_only`
        """
        parts = urlsplit(routed_url)
        if path_only:
            return parts.path

        for pattern, cls in self.get_subdomain_routing_mapping().items():
            full_pattern = "%s.%s" % (pattern, subdomains.utils.get_domain())
            match = re.match(full_pattern, parts.netloc)
            if match is not None:
                domain = self.get_unrouted_domain_by_match(**match.groupdict())
                break
        else:
            domain = subdomains.utils.get_domain()

        return urlunsplit((
            self.get_remote_request_scheme(),
            domain,
            parts.path,
            parts.query,
            parts.fragment))

    @xframe_options_exempt
    def route_request(self, request):
        """
        Route the request to the remote server.

        :param request: Incoming request to route
        :type request: :py:class:`django.http.HttpRequest`
        :return: The routed response
        :rtype: :py:class:`django.http.HttpResponse`
        """
        self.request = request
        self.debug("Incoming request: %s %s://%s%s" % (
            request.method, request.scheme, request.get_host(), request.path_info))
        self.remote_session.cookies = self.get_remote_request_cookiejar()
        remote_response = self.get_remote_response()
        response = self.get_response(remote_response)
        return response

    def get_remote_response(self):
        """
        Send the request to the remote domain and return the response.
        """
        url = "%s://%s%s" % (
            self.get_remote_request_scheme(),
            self.get_remote_request_host(), self.get_remote_request_path())
        response = self.remote_session.request(
            method=self.get_remote_request_method(),
            allow_redirects=False,
            data=self.get_remote_request_body(),
            headers=self.get_remote_request_headers(),
            url=url)
        self.debug_http_package(response.request, label='Remote request.')
        self.debug_http_package(response, label='Remote response.')
        return response

    def get_remote_request_method(self):
        method = self.request.method
        return method

    def get_remote_request_scheme(self):
        scheme = self.request.scheme
        return scheme

    def get_remote_request_host(self):
        return urlsplit(self.get_unrouted_url(
            "%s://%s" % (self.request.scheme, self.request.get_host()),
            path_only=False)).netloc

    def get_remote_request_path(self):
        path = self.request.path_info
        if self.request.META.get("QUERY_STRING", "") != "":
            path = "%s?%s" % (path, self.request.META["QUERY_STRING"])
        return path

    def get_remote_request_cookiejar(self):
        from .models import ServerCookiejar
        server_cj, created = ServerCookiejar.objects.get_or_create(
            user=self.request.user)
        if created:
            from requests.utils import cookiejar_from_dict
            cookiejar = cookiejar_from_dict({})
        else:
            try:
                cookiejar = pickle.loads(server_cj.contents)
            except EOFError:
                from requests.utils import cookiejar_from_dict
                cookiejar = cookiejar_from_dict({})
        return cookiejar

    def get_remote_request_headers(self):
        headers = {}
        convert_fn = lambda s: s.replace("_", "-").lower()
        for header, value in self.request.META.items():
            if header == 'HTTP_COOKIE':
                pass
            elif header == "CONTENT_TYPE":
                headers[convert_fn(header)] = value
            elif header == "HTTP_HOST":
                value = self.get_remote_request_host()
                headers[convert_fn(header[5:])] = value
            elif header == "HTTP_REFERER":
                value = self.get_unrouted_url(value, path_only=False)
                headers[convert_fn(header[5:])] = value
            elif header == "HTTP_ACCEPT_ENCODING" and value != "*":
                if "gzip" not in value and "deflate" not in value:
                    value = "gzip, deflate, %s" % (value,)
                headers[convert_fn(header[5:])] = value
            elif header[:5] == "HTTP_":
                headers[convert_fn(header[5:])] = value

        if 'accept-encoding' not in headers:
            headers['accept-encoding'] = "gzip, deflate"

        return headers

    def get_remote_request_body(self):
        body = self.request.body
        return body

    def get_response(self, remote_response):
        response_content = self.get_response_content(remote_response)
        response_content = self.alter_response_content(
            response_content, remote_response)
        response = HttpResponse(
            self.get_response_body(response_content),
            status=remote_response.status_code,
            content_type=remote_response.headers.get('content-type'))
        self.alter_response(response, remote_response)
        return response

    def get_response_content(self, remote_response):
        content_type = remote_response.headers.get('content-type', '')
        if "html" in content_type:
            return BeautifulSoup(remote_response.text, 'lxml')
        elif "text" in content_type or "javascript" in content_type:
            return remote_response.text
        elif "json" in content_type:
            return remote_response.text
        else:
            return remote_response.content

    def get_response_body(self, response_content):
        if isinstance(response_content, BeautifulSoup):
            return response_content.prettify()
        elif isinstance(response_content, bytes):
            return response_content
        else:
            return str(response_content)

    def alter_response_content(self, response_content, remote_response):
        return response_content

    def alter_response(self, response, remote_response):
        self.alter_response_cookies(response, remote_response)
        for header, value in self.get_response_headers(remote_response).items():
            response[header] = value

    def get_response_headers(self, remote_response):
        headers = {}
        ignore_list = ["x-frame-options", "set-cookie"]
        for header, value in remote_response.headers.items():
            header = header.lower()
            if header == "location":
                value = self.get_routed_url(value, path_only=False)
                headers[header.title()] = value
                self.debug("Redirecting to %s" % (value,))
            elif header == "content-encoding" and value in ["gzip", "deflate"]:
                # Content compressed in gzip or deflate is automatically
                # unpacked by the requests libary. For it to be packed
                # later on, this header must not be already set.
                continue
            elif header == "content-security-policy":
                if 'frame-ancestors' in value:
                    if 'HTTP_REFERER' in self.request.META:
                        value = value.replace(
                            "frame-ancestors",
                            "frame-ancestors %s" % (
                                self.request.META['HTTP_REFERER'],))
                headers[header.title()] = value
            elif header in ignore_list:
                continue
            else:
                headers[header.title()] = value
        return headers

    def alter_response_cookies(self, response, remote_response):
        """
        Alter the response send back to the user by setting cookies, if any.
        """
        # Cookies beloning to this user are kept at the server.
        # Since this will also be the last moment we'll need it in this request,
        # let's store the changes in the server cookiejar.
        from .models import ServerCookiejar
        server_cj, _ = ServerCookiejar.objects.get_or_create(
            user=self.request.user)
        server_cj.contents = pickle.dumps(self.remote_session.cookies)
        server_cj.save()


class StaticFileMixin():

    def route_request(self, request):
        static_extensions = ['jpg','png','css','jpeg','gif', 'svg', 'js']
        filename_parts = request.path_info.split('.')
        if filename_parts and filename_parts[-1] in static_extensions:
            self.request = request
            url = "%s://%s%s" % (
                self.get_remote_request_scheme(),
                self.get_remote_request_host(), self.get_remote_request_path())
            self.debug("Redirecting request to remote host.")
            return HttpResponseRedirect(url)
        return super().route_request(request)


class Router(StaticFileMixin, BaseRouter):

    @classmethod
    def get_subdomain_patterns(cls):
        """
        Return a tuple of subdomain pattern strings that should be handled by
        this router class.

        :rtype: tuple of regex strings
        """
        return (r"(?P<domain_hash>[A-Za-z2-7-]+)-rtr",)


class AppRouter(Router):
    """
    Router class for remote severs proving apps.

    :param app: The application it is routing a request for.
    :type app: :py:class:`loader.models.App`
    """

    def __init__(self, app, remote_domain=None, *args, **kwargs):
        self.app = app
        if remote_domain is None:
            kwargs['remote_domain'] = urlsplit('http://'+self.app.root).netloc
        else:
            kwargs['remote_domain'] = remote_domain
        super().__init__(*args, **kwargs)

    @classmethod
    def get_routed_app_url(cls, request, app, location='/'):
        router = cls(app)
        router.request = request
        return router.get_routed_url(location, path_only=False)

    @classmethod
    @xframe_options_exempt
    def route_path_by_subdomain(cls, request, domain_hash):
        from kb.apps.models import App
        try:
            domain, app_id = cls.unpack_secure_token(domain_hash)
        except ValueError:
            cls.debug("Router could not unpack domain token")
            raise Http404()

        cls.debug("Router matched domain %s of app %s" % (domain, app_id))
        try:
            app = App.objects.get(pk=app_id)
        except App.DoesNotExist:
            raise Http404
        else:
            router = cls(app, remote_domain=domain)
            return router.route_request(request)

    @classmethod
    def get_subdomain_patterns(cls):
        return (r"(?P<domain_hash>[A-Za-z2-7-]+)-app",)

    def get_remote_response(self):
        """
        Send the request to the remote domain and return the response.
        """
        if self.app_login_needed():
            self.debug("[App Login] Starting login procedure")
            status = self.app_login()
            self.debug("[App Login] Successful?: %s" % (status,))
        return super().get_remote_response()

    def alter_response_content(self, response_content, remote_response):
        if isinstance(response_content, BeautifulSoup):
            adaptor = self.get_app_adaptor()
            if adaptor is not None:
                app_script = adaptor.get_app_script()
                if app_script is not None:
                    response_content.body.append(response_content.new_tag(
                        'script', scr=app_script))
        return response_content

    def get_remote_request_scheme(self):
        scheme = self.app.scheme
        return scheme

    def get_routed_domain(self, url):
        """
        Return a routed version of the domain in ``url``.

        :param str url: The url that contains the domain that will be routed
        :return: a routed domain string
        """
        parts = urlsplit(url)
        netloc = parts.netloc or self.remote_domain
        if re.match(self.app.identical_urls, netloc):
            return "%s-app.%s" % (
                self.pack_secure_params((netloc, self.app.pk)),
                subdomains.utils.get_domain())
        else:
            return super().get_routed_domain(url)

    def get_app_adaptor(self):
        from importlib import import_module
        if not self.app.adaptor_class:
            return None

        adaptor_path = self.app.adaptor_class.split('.')
        adaptor_module = ".".join(adaptor_path[:-1])
        if adaptor_module:
            try:
                adaptor = getattr(import_module(adaptor_module),
                    adaptor_path[-1])
            except ImportError:
                self.debug('Cannot find adaptor module.')
                return None
            except AttributeError:
                self.debug('Cannot find adaptor class in module.')
                return None
        else:
            try:
                adaptor = globals()[adaptor_path[-1]]
            except KeyError:
                self.debug("Cannot find adaptor class in globals")
                return None
        return adaptor

    def app_login_needed(self):
        adaptor = self.get_app_adaptor()
        if adaptor is not None:
            return adaptor.is_logged_in(
                user=self.request.user,
                session=self.remote_session,
                app=self.app)

        config = self.app.login_config
        if 'check' not in config or 'method' not in config['check']:
            return False
        if config['check']['method'] == 'PING_REDIRECT':
            if 'url' not in config['check']:
                return False
            response = self.remote_session.request(method="HEAD",
                                                   url=config['check']['url'],
                                                   allow_redirects=False)

            # Debug the interaction
            self.debug_http_package(response.request,
                    label='Login check request')
            self.debug_http_package(response, label='Login check response')
            return response.status_code == 302
        elif config['check']['method'] == 'FETCH_AND_SEARCH':
            if 'url' not in config['check'] or 'search' not in config['check']:
                return False
            response = self.remote_session.request(method="GET",
                                                   url=config['check']['url'])
            # Debug the interaction
            self.debug_http_package(response.request,
                    label='Login check request')
            self.debug_http_package(response, label='Login check response')
            return config['check']['search'] in response.text
        else:
            return False

    def app_signup(self):
        """
        Perform automatic app signup based on signup script.
        """
        adaptor = self.get_app_adaptor()
        if adaptor is not None:
            return adaptor.signup(
                user=self.request.user,
                session=self.remote_session,
                app=self.app)
        config = self.app.login_config
        cookiejar = self.remote_session.cookies
        if 'signup' not in config or 'post' not in config['signup']:
            return False
        # Execute signup script
        signup_document = None
        signup_url = "%s://%s%s" % (
            self.app.scheme, self.app.root, config['signup']['post'])
        if 'form' in config['signup']:
            signup_document_url = "%s://%s%s" % (
                self.app.scheme, self.app.root, config['signup']['form'])
        else:
            signup_document_url = signup_url
        signup_variables = {}
        signup_payload = {}
        signup_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': '%s://%s' % (self.app.scheme, self.app.root),
            'User-Agent': (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                "(KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"),
            'Referer': signup_url}
        # Generate user credentials
        from .models import ServerCredentials
        if 'check-username' in config['signup']:
            username_valid = False
            invalid_usernames = []
            while not username_valid:
                credentials = ServerCredentials.generate(
                    app=self.app,
                    user=self.request.user,
                    invalid_usernames=invalid_usernames)
                check_username = config['signup']['check-username']
                if check_username['method'] == "GET_EXACT_MATCH":
                    check_username_result = self.remote_session.request(
                        method="GET",
                        url=check_username['url'].replace(
                            "$username", credentials.username))
                    check_username_match_value = \
                            check_username['match'].replace(
                                "$username", credentials.username)
                    if check_username_result.text == \
                            check_username_match_value:
                        username_valid = True
                    else:
                        invalid_usernames.append(credentials.username)
                else:
                    break

            signup_variables['username'] = credentials.username
            signup_variables['password'] = credentials.password
        else:
            credentials = ServerCredentials.generate(
                    app=self.app, user=self.request.user)
            signup_variables['username'] = credentials.username
            signup_variables['password'] = credentials.password

        # TODO: Set user fields as signup variables (name, email, birthday, etc)
        secret_body_values = [credentials.username, credentials.password]

        # Retrieve the head of the signup page for cookies
        signup_document_response = self.remote_session.request(
            url=signup_document_url, method="GET")

        if 'heads' in config['signup']:
            for url in config['signup']['heads']:
                self.remote_session.request(url=url, method="HEAD")

        if 'vars' in config['signup']:
            for name, value in config['signup']['vars'].items():
                if value[:7] == "cookie:" and value[7:] in cookiejar:
                    signup_variables[name] = cookiejar[value[7:]]
                elif value[:6] == "field:":
                    if signup_document is None:
                        if signup_document_response.status_code != 200:
                            self.debug(
                                "Retrieving signup document for field"
                                "retrieval failed.")
                            continue
                        signup_document = BeautifulSoup(
                            signup_document_response.text)
                    field = signup_document.find('input',
                                                attrs={"name": value[6:]})
                    if field is not None and field.has_attr('value'):
                        signup_variables[name] = field['value']
                else:
                    signup_variables[name] = value

        if 'payload' in config['signup']:
            for name, value in config['signup']['payload'].items():
                if value == "":
                    signup_payload[name] = ""
                elif isinstance(value, str) and value[0] == "$" \
                        and value[1:] in signup_variables:
                    signup_payload[name] = signup_variables[value[1:]]
                else:
                    signup_payload[name] = value

        if 'headers' in config['signup']:
            for name, value in config['signup']['headers'].items():
                if isinstance(value, str) and value[0] == "$" \
                        and value[1:] in signup_variables:
                    signup_headers[name] = signup_variables[value[1:]]
                else:
                    signup_headers[name] = value

        # Construct and execute signup request
        request_params = {
            "method":"POST",
            "allow_redirects":False,
            "headers":signup_headers,
            "url":signup_url}
        if 'Content-Type' in signup_headers and \
                signup_headers['Content-Type'] == "application/json":
            request_params['json'] = signup_payload
        else:
            request_params['data'] = signup_payload
        response = self.remote_session.request(**request_params)

        # Debug the interaction
        self.debug_http_package(response.request, label='Signup request',
                secret_body_values=secret_body_values)
        self.debug_http_package(response, label='Signup response')
        if not self.app_login_needed():
            credentials.save()
            return True
        elif self.app_login(credentials=credentials):
            credentials.save()
            return True
        else:
            return False

    def app_login(self, credentials=None):
        """
        Perform automatic app login based on login script.
        """
        from .models import ServerCredentials
        try:
            credentials = ServerCredentials.objects.get(
                app=self.app, user=self.request.user)
        except ServerCredentials.DoesNotExist:
            self.debug("No credentials found for this app.")
            credentials = None

        if credentials is None:
            if self.app_signup():
                self.debug("Retrying credentials after signup")
                try:
                    credentials = ServerCredentials.objects.get(
                        app=self.app, user=self.request.user)
                except ServerCredentials.DoesNotExist:
                    self.debug("No credentials found for this app.")
                    credentials = None

        adaptor = self.get_app_adaptor()
        if adaptor is not None:
            return adaptor.login(
                credentials=credentials,
                user=self.request.user,
                session=self.remote_session,
                app=self.app)

        config = self.app.login_config
        cookiejar = self.remote_session.cookies
        if 'login' not in config or 'post' not in config['login']:
            return False
        # Execute login script
        login_document = None
        login_url = "%s://%s%s" % (
            self.app.scheme, self.app.root, config['login']['post'])
        login_variables = {}
        login_payload = {}
        login_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': '%s://%s' % (self.app.scheme, self.app.root),
            'User-Agent': (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                "(KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"),
            'Referer': login_url}

        if credentials is None:
            secret_body_values = None
        else:
            login_variables['username'] = credentials.username
            login_variables['password'] = credentials.password
            secret_body_values = [credentials.username, credentials.password]

        # Retrieve the head of the login page for cookies
        login_document_response = self.remote_session.request(
            url=login_url, method="GET")

        if 'heads' in config['login']:
            for url in config['login']['heads']:
                self.remote_session.request(url=url, method="HEAD")

        if 'vars' in config['login']:
            for name, value in config['login']['vars'].items():
                if value[:7] == "cookie:" and value[7:] in cookiejar:
                    login_variables[name] = cookiejar[value[7:]]
                elif value[:6] == "field:":
                    if login_document is None:
                        if login_document_response.status_code != 200:
                            self.debug(
                                "Retrieving login document for field"
                                "retrieval failed.")
                            continue
                        login_document = BeautifulSoup(
                            login_document_response.text)
                    field = login_document.find('input',
                                                attrs={"name": value[6:]})
                    if field is not None and field.has_attr('value'):
                        login_variables[name] = field['value']
                else:
                    login_variables[name] = value

        if 'payload' in config['login']:
            for name, value in config['login']['payload'].items():
                if value == "":
                    login_payload[name] = ""
                elif isinstance(value, str) and value[0] == "$" \
                        and value[1:] in login_variables:
                    login_payload[name] = login_variables[value[1:]]
                else:
                    login_payload[name] = value

        if 'headers' in config['login']:
            for name, value in config['login']['headers'].items():
                if isinstance(value, str) and value[0] == "$" \
                        and value[1:] in login_variables:
                    login_headers[name] = login_variables[value[1:]]
                else:
                    login_headers[name] = value

        # Construct and execute login request
        request_params = {
            "method":"POST",
            "allow_redirects":False,
            "headers":login_headers,
            "url":login_url}
        if 'Content-Type' in login_headers and \
                login_headers['Content-Type'] == "application/json":
            request_params['json'] = login_payload
        else:
            request_params['data'] = login_payload
        response = self.remote_session.request(**request_params)

        # Debug the interaction
        self.debug_http_package(response.request, label='Login request',
                secret_body_values=secret_body_values)
        self.debug_http_package(response, label='Login response')
        if response.status_code == 302:
            return True
        else:
            return not self.app_login_needed()
