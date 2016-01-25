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
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit, quote, unquote

from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import ServerCookiejar

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

    def debug(self, msg):
        """
        Prints a debug message when the setting ``DEBUG`` is set to True.
        Each debug message is preprended with the current time provided by
        :func:`datetime.datetime.now` and the class name."

        :param str msg: The debug message to display
        """
        if not settings.DEBUG:
            return
        print("[%s] %s - %s" % (datetime.now(), self.__class__.__name__, msg))

    @classmethod
    @xframe_options_exempt
    def route_path_by_subdomain(cls, request, domain):
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
        return "%s.rtr.%s" % (netloc, subdomains.utils.get_domain())

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
        return kwargs.get('domain', subdomains.utils.get_domain())

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
        self.debug("Response: HTTP %d, Content-length: %d" % (
            response.status_code, len(response.content)))
        return response

    def get_remote_response(self):
        """
        Send the request to the remote domain and return the response.
        """
        url = "%s://%s%s" % (
            self.get_remote_request_scheme(),
            self.get_remote_request_host(), self.get_remote_request_path())
        self.debug("%s: %s %s" % ("Remote request", self.request.method, url))
        return self.remote_session.request(
            method=self.get_remote_request_method(),
            allow_redirects=False,
            data=self.get_remote_request_body(),
            headers=self.get_remote_request_headers(),
            url=url)

    def get_remote_request_method(self):
        method = self.request.method
        self.debug("Remote request method: %s" % (method,))
        return method

    def get_remote_request_scheme(self):
        scheme = self.request.scheme
        self.debug("Remote request scheme: %s" % (scheme,))
        return scheme

    def get_remote_request_host(self):
        return urlsplit(self.get_unrouted_url(
            "%s://%s" % (self.request.scheme, self.request.get_host()),
            path_only=False)).netloc

    def get_remote_request_path(self):
        path = self.request.path_info
        if self.request.META.get("QUERY_STRING", "") != "":
            path = "%s?%s" % (path, self.request.META["QUERY_STRING"])
        self.debug("Remote request path: %s" % (path,))
        return path

    def get_remote_request_cookiejar(self):
        server_cj, created = ServerCookiejar.objects.get_or_create(
            user=self.request.user)
        if created:
            from requests.utils import cookiejar_from_dict
            cookiejar = cookiejar_from_dict({})
        else:
            cookiejar = pickle.loads(server_cj.contents)
        self.debug("Remote request cookiejar: %s" % (cookiejar,))
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

        self.debug("Remote request headers: %s" % (headers,))
        return headers

    def get_remote_request_body(self):
        body = self.request.body
        self.debug("Remote request body: %s..." % (body[:20],))
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
        if response.has_header('Set-Cookie'):
            self.debug("Response Cookies (after alter): %s" % (response['Set-Cookie'],))
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
            elif header in ignore_list:
                continue
            else:
                headers[header.title()] = value
        return headers

    def alter_response_cookies(self, response, remote_response):
        """
        Alter the response send back to the user by setting cookies, if any.
        """
        self.debug("Cookies retrieved from remote: %s" % (
                self.remote_session.cookies))
        # Cookies beloning to this user are kept at the server.
        # Since this will also be the last moment we'll need it in this request,
        # let's store the changes in the server cookiejar.
        server_cj, _ = ServerCookiejar.objects.get_or_create(
            user=self.request.user)
        server_cj.contents = pickle.dumps(self.remote_session.cookies)
        server_cj.save()


class GoogleMixin():

    def get_remote_request_path(self):
        path = super().get_remote_request_path()

        if self.remote_domain == "accounts.google.com" and \
                self.request.path_info == "/o/oauth2/postmessageRelay":
            routed_url = unquote(self.request.GET.get("parent", ''))
            unrouted_url = self.get_unrouted_url(routed_url, path_only=False)
            self.debug("Swapping %s with %s" % (
                quote(routed_url, safe=""),
                quote(unrouted_url, safe="")))
            return re.sub(
                quote(routed_url, safe=""), quote(unrouted_url, safe=""), path)
        elif self.remote_domain == "accounts.google.com" and \
                self.request.path_info == "/o/oauth2/auth":
            routed_url = unquote(self.request.GET.get("origin", ''))
            unrouted_url = self.get_unrouted_url(routed_url, path_only=False)
            self.debug("Swapping %s with %s" % (
                quote(routed_url, safe=""),
                quote(unrouted_url, safe="")))
            return re.sub(
                quote(routed_url, safe=""), quote(unrouted_url, safe=""), path)
        elif self.remote_domain == "accounts.google.com" and \
                self.request.path_info == "/ServiceLogin":
            unrouted_url = unquote(self.request.GET.get("continue", ''))
            if unrouted_url == "":
                return path
            routed_url = self.get_routed_url(unrouted_url, path_only=False)
            self.debug("Swapping %s with %s" % (
                quote(unrouted_url, safe=""),
                quote(routed_url, safe="")))
            return re.sub(
                quote(unrouted_url, safe=""), quote(routed_url, safe=""), path)
        elif self.remote_domain == "accounts.google.com" and \
                self.request.path_info == "/LoginVerification":
            unrouted_url = unquote(self.request.GET.get("continue", ''))
            if unrouted_url == "":
                return path
            routed_url = self.get_routed_url(unrouted_url, path_only=False)
            self.debug("Swapping %s with %s" % (
                quote(unrouted_url, safe=""),
                quote(routed_url, safe="")))
            return re.sub(
                quote(unrouted_url, safe=""), quote(routed_url, safe=""), path)
        elif self.remote_domain == "appengine.google.com" and \
                self.request.path_info == "/_ah/conflogin":
            unrouted_url = unquote(self.request.GET.get("continue", ''))
            if unrouted_url == "":
                return path
            routed_url = self.get_routed_url(unrouted_url, path_only=False)
            self.debug("Swapping %s with %s" % (
                quote(unrouted_url, safe=""),
                quote(routed_url, safe="")))
            return re.sub(
                quote(unrouted_url, safe=""), quote(routed_url, safe=""), path)
        else:
            return path

    def alter_response_content(self, response_content, remote_response):
        response_content = super().alter_response_content(
            response_content, remote_response)
        if self.remote_domain == "apis.google.com" and \
                "javascript" in remote_response.headers.get('content-type', ''):
            pattern = r"(['\"])https://accounts.google.com/o/([^'\"]+)['\"]"
            domain = self.get_routed_domain("https://accounts.google.com")
            replacement = r"\1https://%s/o/\2\1" % (domain,)
            response_content = re.sub(pattern, replacement, response_content)
        elif self.remote_domain == "accounts.google.com" and \
                self.request.method == "GET":
            if not isinstance(response_content, BeautifulSoup):
                return response_content
            for form in response_content.find_all('form'):
                if 'action' not in form.attrs:
                    continue
                form['action'] = self.get_routed_url(
                    form['action'],
                    path_only=False)
            for link in response_content.find_all('a'):
                if 'href' not in link.attrs:
                    continue
                link['href'] = self.get_routed_url(link['href'])
        elif isinstance(response_content, BeautifulSoup):
            pattern_gapis = r"(['\"])https://apis.google.com/js/([^'\"]+)['\"]"
            domain = self.get_routed_domain("https://apis.google.com")
            replacement_gapis = r"\1https://%s/js/\2\1" % (domain,)
            for script in response_content.find_all('script'):
                script.string = re.sub(
                    pattern_gapis, replacement_gapis, str(script.string))

        return response_content


class Router(GoogleMixin, BaseRouter):

    @classmethod
    def get_subdomain_patterns(cls):
        """
        Return a tuple of subdomain pattern strings that should be handled by
        this router class.

        :rtype: tuple of regex strings
        """
        return (r"(?P<domain>.+)\.rtr",)


class AppRouter(Router):
    """
    Router class for remote severs proving apps.

    :param app: The application it is routing a request for.
    :type app: :py:class:`loader.models.App`
    """

    def __init__(self, app, *args, **kwargs):
        self.app = app
        kwargs['remote_domain'] = urlsplit('http://'+self.app.root).netloc
        super().__init__(*args, **kwargs)

    @classmethod
    def get_routed_app_root(cls, request, app):
        router = cls(app)
        router.request = request
        return router.get_routed_url(
            "%s://%s" % (app.scheme, app.root), path_only=False)

    @classmethod
    @xframe_options_exempt
    def route_path_by_subdomain(cls, request, domain):
        from kb.apps.models import App
        try:
            app = App.objects.get(root=domain)
        except App.DoesNotExist:
            for app in App.objects.exclude(identical_urls=""):
                if re.match(app.identical_urls, domain):
                    break
            else:
                app = None

        if app is None:
            raise Http404
        else:
            router = cls(app)
            return router.route_request(request)

    @classmethod
    def get_subdomain_patterns(cls):
        return (r"(?P<domain>.+)\.app",)

    def get_remote_response(self):
        """
        Send the request to the remote domain and return the response.
        """
        if self.app_login_needed:
            status = self.app_login()
            self.debug("Login was successful: %s" % (status,))
        return super().get_remote_response(request)

    def get_routed_domain(self, url):
        """
        Return a routed version of the domain in ``url``.

        :param str url: The url that contains the domain that will be routed
        :return: a routed domain string
        """
        parts = urlsplit(url)
        netloc = parts.netloc or self.remote_domain
        if re.match(self.app.identical_urls, netloc):
            return "%s.app.%s" % (parts.netloc, subdomains.utils.get_domain())
        else:
            return super().get_routed_domain(url)

    def app_login_needed(self):
        config = self.app.login_config
        if 'check' not in config or 'method' not in config['check']:
            return False
        if config['check']['method'] == 'PING_REDIRECT':
            if 'url' not in config['check']:
                return False
            response = self.remote_session.request(method="HEAD",
                                                   url=config['check']['url'],
                                                   allow_redirect=False)
            return response.status_code == 302
        else:
            return False

    def app_login(self):
        """
        Perform automatic app login based on login script.
        """
        config = self.app.login_config
        cookiejar = self.remote_session.cookies
        if 'login' not in config or 'post' not in config['login']:
            return False
        else:
            self.debug("Executing login script for app.")
        # Execute login script
        login_document = None
        login_url = "%s://%s%s" % (
            self.app.scheme, self.app.root, config['login'])
        login_variables = {}
        login_payload = {}
        login_headers = {}
        # Retrieve user credentials
        from .models import ServerCredentials
        try:
            credentials = ServerCredentials.objects.get(
                app=self.app, user=self.request.user)
        except ServerCredentials.DoesNotExist:
            self.debug("No credentials found for this app.")
        else:
            login_variables['username'] = credentials.username
            login_variables['password'] = credentials.password

        if 'vars' in config['login']:
            for name, value in config['login']['vars'].items():
                if value[:7] == "cookie:" and value[7:] in cookiejar:
                    login_variables[name] = cookiejar[value[7:]]
                elif value[:6] == "field:":
                    if login_document is None:
                        response = requests.get(login_url)
                        if response.status_code != 200:
                            continue
                        login_document = BeautifulSoup(response.text)
                    field = login_document.find('input',
                                                attrs={"name": value[6:]})
                    if field is not None and field.has_attr('value'):
                        login_variables[name] = field['value']
                else:
                    login_variables[name] = value
        self.debug(("[App login] vars: %s" % (
            login_variables,)).replace(credentials.password, "****"))
        if 'payload' in config['login']:
            for name, value in config['login']['payload'].items():
                if value[0] == "$" and value[1:] in login_variables:
                    login_payload[name] = login_variables[value[1:]]
                else:
                    login_payload[name] = value
        self.debug(("[App login] payload: %s" % (
            login_payload,)).replace(credentials.password, "****"))
        if 'headers' in config['login']:
            for name, value in config['login']['headers'].items():
                if value[0] == "$" and value[1:] in login_variables:
                    login_headers[name] = login_variables[value[1:]]
                else:
                    login_headers[name] = value
        self.debug(("[App login] headers: %s" % (
            login_headers,)).replace(credentials.password, "****"))
        # Execute login request
        response = self.remote_session.request(
            method="POST",
            allow_redirects=False,
            data=login_payload,
            headers=login_headers,
            url=login_url)
        self.debug("[App login] Response code from login: %d"  % (
            response.status_code,))
        if response.status_code == 302:
            return True
        else:
            return self.app_login_needed()


class DuolingoAppRouter(AppRouter):

    @classmethod
    def get_subdomain_patterns(cls):
        return (r"(?P<domain>.+\.duolingo\.com)\.app",)
