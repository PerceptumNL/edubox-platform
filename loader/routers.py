"""
Routing local requests to remote servers
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

    :param str remote_host: The hostname of the remote sever.
    """

    def __init__(self, remote_host):
        self.remote_host = remote_host

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
    def get_subdomain_patterns(cls):
        """
        Return a tuple of subdomain pattern strings that should be handled by
        this router class.
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
            mapping[pattern] = cls.route_path_by_subdomain
        # Add subdomain patterns of subclasses
        for subclass in cls.__subclasses__():
            mapping.update(subclass.get_subdomain_routing_mapping())
        return mapping

    def reroute(self, url, path_only=True):
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
            return urlunsplit(
                    self.request.scheme,
                    self.get_router_domain(url),
                    parts.path,
                    parts.query,
                    parts.fragment)

    def get_routed_domain(self, url):
        parts = urlsplit(url)
        netloc = parts.netloc or '_'
        return "%s.rtr.%s" % (parts.netloc, subdomains.utils.get_domain())

    def get_unrouted_domain_by_match(self, **kwargs):
        return kwargs.get('domain', subdomains.utils.get_domain())

    def unroute(self, routed_url, path_only=True):
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

        for pattern, cls in self.__class__.get_subdomain_routing_mapping():
            match = re.match(pattern, "%s.%s" % (parts.netloc,
                subdomains.utils.get_domain()))
            if match is not None:
                domain = cls.get_unrouted_domain(**match.groupdict())
                break;
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
            request.method, request.scheme, request.path_info ))
        remote_response = self.get_remote_response()
        response = self.get_response(remote_response)
        self.debug("Response: HTTP %d, Content-length: %d" % (
            response.status_code, len(response.body)))
        return response

    def get_remote_response(self):
        self.remote_session = requests.Session()
        self.remote_session.cookies = self.get_remote_request_cookiejar()
        url = "%s://%s%s" % (self.get_remote_request_scheme(),
                self.get_remote_request_host(), self.get_remote_request_path())
        self.debug("Remote request", self.request.method, url)
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
        return self.remote_host

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
        convert_fn = lambda s: s.replace("_","-").lower()
        for header, value in self.request.META.items():
            if header == "CONTENT_TYPE":
                headers[convert_fn(header)] = value
            elif header == "HTTP_HOST":
                value = self.get_remote_request_host()
                headers[convert_fn(header[5:])] = value
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
        content_type = remote_response.headers.get('content-type','')
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
        for header,value in self.get_response_headers(remote_response).items():
            response[header] = value

    def get_response_headers(self, remote_response):
        headers = {}
        for header, value in self.remote_response.headers.items():
            header = header.lower()
            #TODO: Extend list
            if header == "content-type":
                headers[header.title()] = value
            elif header == "location":
                headers[header.title()] = value
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
                    path=self.reroute(cookie.path, path_only=True))

class AppRouter(Router):
    """
    Router class for remote severs proving apps.

    :param app: The application it is routing a request for.
    :type app: :py:class:`loader.models.App`
    """

    def __init__(self, app, *args, **kwargs):
        self.app = app
        kwargs['remote_host'] = self.app.root
        super().__init__(*args, **kwargs)

    @classmethod
    def get_subdomain_patterns(cls):
        return (r"(?P<app_domain>.+)\.app",)

    def reroute(self, url, path_only=True, pattern="app_routing"):
        if self.domain_routing:
            return url
        else:
            return reverse(pattern, args=(self.app.pk, url))

    def unroute(self, routed_url):
        try:
            match = RegexURLResolver("^/", 'loader.urls').resolve(routed_url)
        except Resolver404:
            return routed_url
        else:
            return match.kwargs.get('path', routed_url)

    def alter_response_content(self, response_content, remote_response):
        pass

    def get_response_headers(self, remote_response):
        headers = super().get_response_headers()
        if 'Location' in headers:
            value = headers['Location']
            if self.app.identical_urls is not None and \
                re.match(self.app.identical_urls, value):
                    value = self.reroute(value)
            headers['Location'] = value
        return headers
