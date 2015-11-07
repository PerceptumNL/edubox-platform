from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import RegexURLResolver, Resolver404

from rest_framework import serializers, viewsets
from bs4 import BeautifulSoup

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
        settings = {}
        app_id = request.outer_resolver_match.kwargs['app_id']
        settings_values = request.user.settings.filter(setting__app__pk=app_id,
            setting__compact=True)
        for value in settings_values:
            settings[str(value.setting)] = value.value
        settings_qd.update(settings)
        request.GET = settings_qd
    # Redirect request to local function
    return match.func(request)

def _remote_routing(request, urlconf, path):
    req = BeautifulSoup(requests.get(urlconf+path).text)
    print(path)
    print(urlconf)
    print("---")
    print(request.get_full_path())
    full_path = request.get_full_path()
    root_path = "/".join(full_path.split('/')[:4])
    print(root_path)
    print("---")
    
    #Simple test to filter forms, should replace all local urls
    [print(x.prettify()) for x in req.findAll('form')]
    
    #needs work, redirects to original pilot.leestmeer now
    for a in req.findAll('a'):
        a['href'] = root_path+a['href']
    print(urlconf)
    
    for b in req.findAll('form'):
        print(b['action'])
        b['action'] = urlconf+b['action']

    for img in req.findAll('img'):
        print(img['src'])
        img['src'] = urlconf+img['src']

    for link in req.findAll('link'):
        print(link['href'])
        link['href'] = urlconf+link['href']

    loaded_req=req

    return render(request, "loader/container.html", {'html':str(req)}) #HttpResponse(str(req))
    

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

def home(request):
    return render(request, "loader/index.html", {})
