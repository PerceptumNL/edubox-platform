from django.conf.urls import url, patterns

from .apps.views import app_list
from .events.views import API


urlpatterns = patterns('',
    url(r'^apps/', app_list),
    url(r'^events/', API.as_view()),
)
