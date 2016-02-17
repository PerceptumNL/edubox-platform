from django.conf.urls import url, patterns
from .views import launch_app, launch_unit

urlpatterns = patterns('',
    url(r'^(?P<group_id>[^/]+)/apps/(?P<app_id>[^/]+)/?', launch_app),
    url(r'^(?P<group_id>[^/]+)/units/(?P<unit_id>[^/]+)/?', launch_unit),
)
