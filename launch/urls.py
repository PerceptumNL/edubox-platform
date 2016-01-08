from django.conf.urls import url, patterns
from .views import launch_app

urlpatterns = patterns('',
    url(r'^(?P<group_id>[^/]+)/(?P<app_id>[^/]+)/?', launch_app),
)
