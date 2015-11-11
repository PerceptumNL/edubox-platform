from django.http import HttpResponse
from django.core.urlresolvers import reverse, RegexURLResolver, Resolver404

from bs4 import BeautifulSoup
from copy import copy
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit
import requests
import re

from loader.models import App, Service

def get_current_app_id(request):
    """Return the id of the current loaded app.
    The app id is extracted from the request context stored by the router.
    """
    return (request.outer_resolver_match.kwargs['app_id'] if
            hasattr(request, 'outer_resolver_match') else None)

def get_current_app(request):
    """Return the App model instance.
    The instance is retrieved using the output of `get_current_app_id`.
    """
    app_id = get_current_app_id(request)
    if app_id is None:
        return None
    try:
        app = App.objects.get(pk=app_id)
    except App.DoesNotExist:
        return None
    else:
        return app

def dispatch_service_request(outer_request, *args, **kwargs):
    # Create Request object
    from requests import Request
    inner_request = Request(*args, **kwargs)

    if inner_request.method is None or inner_request.url is None:
        return ValueError('The request method and url cannot be None.')

    # Match service patttern on request url
    service_match = re.search(r'^service:([^/]+)(/.+)?$', inner_request.url)
    if not service_match:
        raise ValueError('Expecting service pattern in URL.')

    try:
        service = Service.objects.get(pk=service_match.group(1))
    except Service.DoesNotExist:
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound

    scheme = 'https' if outer_request.is_secure() else 'http'
    service_root = "localhost" if service.local else service.root
    service_path = service_match.group(2) or "/"

    inner_request.url = "%s://%s%s" % (scheme, service_root, service_path)

    # Prepare request, either for sending (remote) or for parsing (local)
    prep_request = inner_request.prepare()

    if service.local:
        # Strategy: Fake HTTP request to local endpoint
        environ = {}

        # Copy environ values from current wsgi request,
        #  since most environment values remains the same
        environ = copy(outer_request.environ)

        environ['REQUEST_METHOD'] = prep_request.method

        from urllib.parse import urlparse
        url_parts = urlparse(prep_request.url)
        environ['PATH_INFO'] = url_parts.path
        environ['QUERY_STRING'] = url_parts.query

        content_type = prep_request.headers.get('Content-Type')
        if content_type is not None:
            environ['CONTENT_TYPE'] = content_type

        content_length = prep_request.headers.get('Content-Length')
        if content_length is not None:
            environ['CONTENT_LENGTH'] = content_length

        # Add all headers that start with HTTP_
        for header in prep_request.headers:
            if header[:5] == "HTTP_":
                environ[header] = prep_request.headers[header]

        # Set special wsgi variables
        environ['wsgi.url_scheme'] = url_parts.scheme
        from io import BytesIO
        environ['wsgi.input'] = BytesIO(bytes(prep_request.body, "utf-8"))

        # Generate a Django WSGIRequest object
        from django.core.handlers.wsgi import WSGIRequest
        wsgi_request = WSGIRequest(environ)

        # Resolve local view function
        from django.core.urlresolvers import RegexURLResolver, Resolver404
        try:
            match = RegexURLResolver("^/", service.root).resolve(url_parts.path)
        except Resolver404:
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound()

        # Return response
        return match.func(wsgi_request)
    else:
        from requests import Session
        session = Session()
        response = session.send(prep_request)

        # Convert requests.Reponse object into django.http.HttpResponse object
        from django.http import HttpResponse
        http_response = HttpResponse(
                content=response.text,
                status=response.status_code,
                reason=response.reason,
                content_type=response.headers.get('Content-Type'))

        # Copy the response headers
        for header in response.headers:
            http_response[header] = response.headers.get(header)

        # Copy the response cookies
        if response.cookies is not None:
            jar = response.cookies
            for domain in jar.list_domains():
                for path in jar.list_paths():
                    cookies = jar.get_dict(domain, path)
                    for key in cookies:
                        http_response.set_cookie(key, cookies[key],
                               domain=domain, path=path)

        return http_response

class Router(object):

    def __init__(self, app, *args, **kwargs):
        self.app = app

    def reroute(self, url, pattern="app_routing"):
        return reverse(pattern, args=(self.app.pk, url))

    def unroute(self, route):
        try:
            match = RegexURLResolver("^/", 'loader.urls').resolve(route)
        except Resolver404:
            return route
        else:
            if match.url_name in ('app_routing', 'contained_app'):
                return match.kwargs['path']
            else:
                return route

    def request(self, request, path):
        self.request = request
        self.path = path
        self.session = requests.Session()
        self.session.cookies = requests.utils.cookiejar_from_dict(
                request.COOKIES)
        print("Sending", self.session.cookies)
        url = self.app.root+path
        self.remote_response = self.session.request(
                method=request.method,
                allow_redirects=False,
                data=request.body,
                headers=self.create_request_headers(),
                url=self.app.root+path,
                params=request.GET)
        self.create_response_content()
        if self.remote_response.status_code == 200:
            self.alter_response_content()
        self.response = HttpResponse(self.response_content,
                status=self.remote_response.status_code,
                content_type=self.remote_response.headers.get('content-type'))
        self.alter_response()
        return self.response

    def create_request_headers(self):
        headers = {}
        app_root_parts = urlsplit(self.app.root)
        convert_fn = lambda s: s.replace("_","-").lower()
        for header, value in self.request.META.items():
            if header == "CONTENT_TYPE":
                headers[convert_fn(header)] = value
            elif header[:5] == "HTTP_":
                if header == "HTTP_HOST":
                    value = app_root_parts.netloc
                elif header == "HTTP_REFERER":
                    referer_parts = urlsplit(value)
                    value = urlunsplit((
                        app_root_parts.scheme,
                        app_root_parts.netloc,
                        self.unroute(referer_parts.path),
                        referer_parts.query,
                        referer_parts.fragment))
                headers[convert_fn(header[5:])] = value
        return headers

    def create_response_content(self):
        content_type = self.remote_response.headers.get('content-type','')
        if "html" in content_type:
            self.response_content = BeautifulSoup(self.remote_response.text, 'lxml')
        elif "image" in content_type:
            self.response_content = self.remote_response.content
        else:
            self.response_content = self.remote_response.text

    def alter_response_content(self):
        if isinstance(self.response_content, BeautifulSoup):
            self.add_document_location_route()
            self.add_serviceworker_route()
            self.update_local_references()
            self.add_jquery_route()
            self.response_content = self.response_content.prettify()

    def alter_response(self):
        self.route_cookies()
        for header,value in self.create_response_headers().items():
            self.response[header] = value

    def route_cookies(self):
        # Cookie transplant
        print('check cookies', self.remote_response.request.method,
                self.remote_response.request.url)
        for cookie in self.session.cookies:
            # TODO: Update server-stored cookiejar for this user
            if cookie.expires is not None:
                expires = datetime.fromtimestamp(cookie.expires)
            else:
                expires = None
            print('set cookie %s=%s' % (cookie.name,cookie.value))
            self.response.set_cookie(
                    cookie.name,
                    cookie.value,
                    expires=expires,
                    path=self.reroute(cookie.path))

    def create_response_headers(self):
        headers = {}
        for header, value in self.remote_response.headers.items():
            header = header.lower()
            #TODO: Extend list
            if header == "content-type":
                headers[header.title()] = value
            elif header == "location":
                if self.app.identical_urls is not None and \
                    re.test(self.app.identical_urls, value):
                        urlparts = urlsplit(value)
                        value = urlunsplit((
                            urlparts.scheme,
                            urlsplit(self.app.root).netloc,
                            self.reroute(urlparts.path),
                            urlparts.query,
                            urlparts.fragment))
                headers[header.title()] = value
        return headers

    def add_document_location_route(self):
        base_route = self.reroute('/')[:-1]
        script_tag = self.response_content.new_tag("script")
        script_tag.string = (
            "window.history.replaceState({},'', "
            "document.location.href.replace('"+base_route+"',''))")
        self.response_content.head.append(script_tag)

    def add_serviceworker_route(self):
        base_route = self.reroute('/')[:-1]
        script_tag = self.response_content.new_tag("script")
        script_tag.string = ("if(navigator != undefined && "
                "navigator.serviceWorker != undefined){ "
            "var __aLSNSrcoDfAJqUe = navigator.serviceWorker.register;"
            "navigator.serviceWorker.register = function(){"
                "if( arguments[0][0] == '/' ){"
                    "arguments[0] = '"+base_route+"'+arguments[0];"
                "}"
                "return __aLSNSrcoDfAJqUe.apply(this, arguments);}}")
        self.response_content.body.append(script_tag)

    def update_local_references(self):
        # Routing <link:href> in head
        try:
            for elem in self.response_content.head.findAll('link'):
                if not 'href' in elem.attrs:
                    continue
                if elem['href'][0] != "h" and elem['href'][0:2] != "//":
                    elem['href'] = self.reroute(elem['href'])
            # Routing <script:src> in head
            for elem in self.response_content.head.findAll('script'):
                if not 'src' in elem.attrs:
                    continue
                if elem['src'][0] != "h" and elem['src'][0:2] != "//":
                    elem['src'] = self.reroute(elem['src'])
            # Routing <link:href> in body
            for elem in self.response_content.body.findAll('link'):
                if not 'href' in elem.attrs:
                    continue
                if elem['href'][0] != "h" and elem['href'][0:2] != "//":
                    elem['href'] = self.reroute(elem['href'])
            # Routing <script:src> in body
            for elem in self.response_content.body.findAll('script'):
                if not 'src' in elem.attrs:
                    continue
                if elem['src'][0] != "h" and elem['src'][0:2] != "//":
                    elem['src'] = self.reroute(elem['src'])
            # Routing <img:src> in body
            for elem in self.response_content.body.findAll('img'):
                if not 'src' in elem.attrs:
                    continue
                if elem['src'][0] != "h" and elem['src'][0:2] != "//":
                    elem['src'] = self.reroute(elem['src'])
            # Routing <a:href> in body
            for elem in self.response_content.body.findAll('a'):
                if not 'href' in elem.attrs:
                    continue
                if elem['href'][0] != "h" and elem['href'][0:2] != "//":
                    elem['href'] = self.reroute(elem['href'])
            # Routing <form:action> in body
            for elem in self.response_content.body.findAll('form'):
                if not 'action' in elem.attrs:
                    continue
                if elem['action'][0] != "h" and elem['action'][0:2] != "//":
                    elem['action'] = self.reroute(elem['action'])
        except Exception as e:
            import q; q.d()

    def add_jquery_route(self):
        base_route = self.reroute('/')[:-1]
        script_tag = self.response_content.new_tag("script")
        script_tag.string = ("if(window.$ != undefined){ "
            "$.ajaxPrefilter(function( options ){"
                "if(options.url[0] == '/'){"
                    "options.url = '"+base_route+"'+options.url; }});}")
        self.response_content.body.append(script_tag)
