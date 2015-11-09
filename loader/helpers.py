from loader.models import App, Service

from bs4 import BeautifulSoup
from copy import copy
import requests
import re

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

    def reroute(self, url):
        return reverse('contained_app', args=(self.app.pk, url))

    def request(self, request, path):
        self.request = request
        self.remote_response = requests.request(
                method=request.method,
                url=app.root+path,
                params=request.GET)
        self.response_document = BeautifulSoup(self.remote_response.text)
        self.response = HttpResponse(self.response_document,
                status=self.remote_response.status_code)
        self.alter_response()
        return self.response

    def alter_response(self):
        self.route_cookies()
        self.update_local_links()

    def route_cookies(self)
        # Cookie transplant
        for cookie in self.remote_response.cookies:
            # TODO: Update server-stored cookiejar for this user
            if cookie.expires is not None:
                expires = datetime.fromtimestamp(cookie.expires)
            else:
                expires = None

            self.response.set_cookie(
                    cookie.name,
                    cookie.value,
                    expires=expires,
                    path=self.reroute(cookie.path))

    def update_local_links(self):
        for a in self.response_document.findAll('a'):
            if a['href'][0] != "h" and a['href'][0:2] != "//":
                a['href'] = self.reroute(a['href'])
