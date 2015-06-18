from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import RegexURLResolver, Resolver404

from rest_framework import serializers, viewsets

import re

from .models import App, Service

class AppSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = App
        fields = ('url', 'title', 'icon', 'load_url')

class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer

class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('url', 'title', 'load_url')

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

def _local_routing(request, urlconf, path):
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
    # Redirect request to local function
    return match.func(request)

def app_routing(request, app_id, path):
    """Redirect request to the referred app's location."""
    app = get_object_or_404(App, pk=app_id)
    if app.local:
        response = _local_routing(request, app.root, path)

        # TODO: Modify response where necessary

        return response
    else:
        # TODO: Write and use _remote_routing function
        return HttpResponse()

def service_routing(request, service_id, path):
    """Redirect request to the referred service' location."""
    service = get_object_or_404(Service, pk=service_id)
    if service.local:
        response = _local_routing(request, service.root, path)

        # TODO: Modify response where necessary

        return response
    else:
        # TODO: Write and use _remote_routing function
        return HttpResponse()
