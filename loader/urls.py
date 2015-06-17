from django.conf.urls import include, url
from rest_framework import routers

from .views import AppViewSet, app_routing, service_routing

index = routers.DefaultRouter()
index.register(r'apps', AppViewSet)

urlpatterns = [
    url(r'^index/?', include(index.urls)),
    url(r'^index/api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
    url(r'^router/apps/(?P<app_id>\d+)', app_routing, name='app_routing'),
    url(r'^router/services/(?P<app_id>\d+)', service_routing,
        name='service_routing')
]
