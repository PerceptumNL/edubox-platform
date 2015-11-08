from django.conf.urls import include, url
from rest_framework import routers

from .views import AppViewSet, ServiceViewSet, app_routing, service_routing

index = routers.DefaultRouter()
index.register(r'apps', AppViewSet)
index.register(r'services', ServiceViewSet)

urlpatterns = [
    url(r'^$', 'loader.views.home'),
    url(r'^app/(?P<app_id>[^/]+)(?P<path>/.*)$', 'loader.views.home',
        name='contained_app'),
    url(r'^index/', include(index.urls)),
    url(r'^index/api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
    url(r'^router/apps/(?P<app_id>[^/]+)(?P<path>/.*)$', app_routing,
        name='app_routing'),
    url(r'^router/services/(?P<service_id>[^/]+)(?P<path>/.*)$', service_routing,
        name='service_routing')
]
