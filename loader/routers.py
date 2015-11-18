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
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse, RegexURLResolver, Resolver404
from bs4 import BeautifulSoup

from copy import copy
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit
import subdomains
import requests
import re

class Router(object):
    """
    Generic base class for all router classes.

    :param str remote_domain: The hostname of the remote sever.
    """

    request = None
    """Incoming request object to be routed."""
    remote_domain = None
    """The remote domain the request must be routed to."""
    remote_sesssion = None
    """The :py:class:`requests.Session` object used for all remote requests."""

    def __init__(self, remote_domain):
        self.remote_domain = remote_domain

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
        return (r"(?P<domain>.+)\.rtr",)

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
        netloc = parts.netloc or '_'
        return "%s.rtr.%s" % (parts.netloc, subdomains.utils.get_domain())

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
            match = re.match(pattern, "%s.%s" % (parts.netloc,
                subdomains.utils.get_domain()))
            if match is not None:
                domain = cls.get_unrouted_domain_by_match(**match.groupdict())
                break
        else:
            domain = subdomains.utils.get_domain()

        return urlunsplit(
                self.get_remote_request_scheme(),
                domain,
                parts.path,
                parts.query,
                parts.fragment)

    def route_request(self, request):
        """
        Route the request to the remote server.

        :param request: Incoming request to route
        :type request: :py:class:`django.http.HttpRequest`
        :return: The routed response
        :rtype: :py:class:`django.http.HttpResponse`
        """
        self.request = request
        self.debug("Incoming request: %s %s://%s" % (
            request.method, request.scheme, request.path_info))
        remote_response = self.get_remote_response()
        response = self.get_response(remote_response)
        self.debug("Response: HTTP %d, Content-length: %d" % (
            response.status_code, len(response.content)))
        return response

    def get_remote_response(self):
        """
        Send the request to the remote domain and return the response.
        """
        self.remote_session = requests.Session()
        self.remote_session.cookies = self.get_remote_request_cookiejar()
        url = "%s://%s%s" % (self.get_remote_request_scheme(),
                self.get_remote_request_host(), self.get_remote_request_path())
        self.debug("%s: %s %s" % ("Remote request", self.request.method, url))
        return self.remote_session.request(
                method=self.get_remote_request_method(),
                allow_redirects=False,
                data=self.get_remote_request_body(),
                headers=self.get_remote_request_headers(),
                url=url,
                params=self.request.GET)

    def get_remote_request_method(self):
        method = self.request.method
        self.debug("Remote request method: %s" % (method,))
        return method

    def get_remote_request_scheme(self):
        scheme = self.request.scheme
        self.debug("Remote request scheme: %s" % (scheme,))
        return scheme

    def get_remote_request_host(self):
        return self.remote_domain

    def get_remote_request_path(self):
        path = self.request.path_info
        self.debug("Remote request path: %s" % (path,))
        return path

    def get_remote_request_cookiejar(self):
        cookiejar = requests.utils.cookiejar_from_dict(self.request.COOKIES)
        self.debug("Remote request cookiejar: %s" % (cookiejar,))
        return cookiejar

    def get_remote_request_headers(self):
        headers = {}
        convert_fn = lambda s: s.replace("_", "-").lower()
        for header, value in self.request.META.items():
            if header == "CONTENT_TYPE":
                headers[convert_fn(header)] = value
            elif header == "HTTP_HOST":
                value = self.get_remote_request_host()
                headers[convert_fn(header[5:])] = value
            elif header == "HTTP_REFERER":
                value = self.get_unrouted_url(value, path_only=False)
        self.debug("Remote request headers: %s" % (headers,))
        return headers

    def get_remote_request_body(self):
        body = self.request.body
        self.debug("Remote request body: %s..." % (body[:20],))
        return body

    def get_response(self, remote_response):
        response_content = self.get_response_content(remote_response)
        self.alter_response_content(response_content, remote_response)
        response = HttpResponse(self.get_response_body(response_content),
                status=remote_response.status_code,
                content_type=remote_response.headers.get('content-type'))
        self.alter_response(response, remote_response)
        return response

    def get_response_content(self, remote_response):
        content_type = remote_response.headers.get('content-type', '')
        if "html" in content_type:
            return BeautifulSoup(remote_response.text, 'lxml')
        elif "image" in content_type:
            return remote_response.content
        else:
            return remote_response.text

    def get_response_body(self, response_content):
        if isinstance(response_content, BeautifulSoup):
            return response_content.prettify()
        else:
            return str(response_content)

    def alter_response_content(self, response_content, remote_response):
        pass

    def alter_response(self, response, remote_response):
        self.alter_response_cookies(response, remote_response)
        for header, value in self.get_response_headers(remote_response).items():
            response[header] = value

    def get_response_headers(self, remote_response):
        headers = {}
        for header, value in remote_response.headers.items():
            header = header.lower()
            #TODO: Extend list
            if header == "content-type":
                headers[header.title()] = value
            elif header == "location":
                value = self.get_routed_url(value, path_only=False)
                headers[header.title()] = value
                self.debug("Redirecting to %s" % (value,))
        return headers

    def alter_response_cookies(self, response, remote_response):
        for cookie in self.remote_session.cookies:
            # TODO: Update server-stored cookiejar for this user
            if cookie.expires is not None:
                expires = datetime.fromtimestamp(cookie.expires)
            else:
                expires = None
            response.set_cookie(
                    cookie.name,
                    cookie.value,
                    expires=expires,
                    path=self.get_routed_url(cookie.path, path_only=True))

class AppRouter(Router):
    """
    Router class for remote severs proving apps.

    :param app: The application it is routing a request for.
    :type app: :py:class:`loader.models.App`
    """

    def __init__(self, app, *args, **kwargs):
        self.app = app
        kwargs['remote_domain'] = self.app.root
        super().__init__(*args, **kwargs)

    @classmethod
    def get_subdomain_patterns(cls):
        return (r"(?P<domain>.+)\.app",)

    def alter_response_content(self, response_content, remote_response):
        pass

    def get_response_headers(self, remote_response):
        headers = super().get_response_headers()
        if 'Location' in headers:
            value = headers['Location']
            if self.app.identical_urls is not None and \
                re.match(self.app.identical_urls, value):
                    value = self.get_routed_url(value)
            headers['Location'] = value
        return headers
