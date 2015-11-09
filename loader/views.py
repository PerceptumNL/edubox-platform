from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import RegexURLResolver, Resolver404, reverse

from rest_framework import serializers, viewsets
from bs4 import BeautifulSoup

from datetime import datetime
import re
import requests

from .models import App, Service

class AppSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = App
        fields = ('id', 'title', 'icon')

class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer

class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('name', 'title')

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

def _local_routing(request, urlconf, path, app=True):
    """Redirect request to a local view."""
    try:
        match = RegexURLResolver("^/", urlconf).resolve(path)
    except Resolver404:
        raise Http404

    # Change path_info of request
    request.path_info = path
    # Recover original script_name
    script_name = re.search(r'^([^/]*)/', request.path).group(0)
    # Reconstruct request path
    request.path = '%s/%s' % (script_name.rstrip('/'),
            path.replace('/', '', 1))
    # Keep outer URL pattern match
    request.outer_resolver_match = request.resolver_match
    # Change URL pattern match
    request.resolver_match = match
    #Add app specific settings for the user
    if not request.user.is_anonymous() and app:
        settings_qd = request.GET.copy()
        """
        settings = {}
        app_id = request.outer_resolver_match.kwargs['app_id']
        settings_values = request.user.settings.filter(setting__app__pk=app_id,
            setting__compact=True)
        for value in settings_values:
            settings[str(value.setting)] = value.value
        settings_qd.update(settings)
        """
        request.GET = settings_qd
    # Redirect request to local function
    return match.func(request)

def _remote_routing(request, urlconf, path):
    """Redirect request to remote web app."""
    app_id = request.resolver_match.kwargs['app_id']
    reroute_fn = lambda url: reverse('contained_app', args=(app_id, url))
    # Construct redirected URL
    redirect_url = urlconf+path
    res = requests.get(urlconf+path)

    req = BeautifulSoup(res.text).body

    req.name = "div"
    req['id'] = "_body"

    for a in req.findAll('a'):
        if a['href'][0] != "h" and a['href'][0:2] != "//":
            a['href'] = reroute_fn(a['href'])
        print repr(a)

    for img in req.findAll('img'):
        img['src'] = reroute_fn(img['src'])
        print img

    for link in req.findAll('link'):
        if link['href'][0] != "h" and link['href'][0:2] != "//":
            link['href'] = reroute_fn(link['href'])
        print link

    http_response = HttpResponse(str(req),
            content_type=res.headers.get('content-type'))

    # Cookie transplant
    for cookie in res.cookies:
        # TODO: Update server-stored cookiejar for this user
        if cookie.expires is not None:
            expires = datetime.fromtimestamp(cookie.expires)
        else:
            expires = None

        http_response.set_cookie(
                cookie.name,
                cookie.value,
                expires=expires,
                path=reverse('contained_app', args=(app_id,cookie.path)))
    return http_response

def app_routing(request, app_id, path):
    """Redirect request to the referred app's location."""
    app = get_object_or_404(App, pk=app_id)
    if app.local:
        response = _local_routing(request, app.root, path)

        # TODO: Modify response where necessary

        return response
    else:
        response = _remote_routing(request, app.root, path) 

        # TODO: Write and use _remote_routing function
        return response

def service_routing(request, service_id, path):
    """Redirect request to the referred service' location."""
    service = get_object_or_404(Service, pk=service_id)
    if service.local:
        response = _local_routing(request, service.root, path, False)

        # TODO: Modify response where necessary

        return response
    else:
        # TODO: Write and use _remote_routing function
        return HttpResponse()

def home(request, *args, **kwargs):
    return render(request, "loader/index.html", {})
