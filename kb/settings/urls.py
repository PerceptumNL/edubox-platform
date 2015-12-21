from django.conf.urls import url, patterns

from .views import *

urlpatterns = patterns('',
    url(r'^(?P<setting_id>[^/]+)/(?P<setting_type>[^/]+)/(?P<value_id>[^/]+)', 
            set_settings),
    url(r'^(?P<setting_id>[^/]+)', get_settings)
)
