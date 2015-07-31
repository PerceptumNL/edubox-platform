from django.conf.urls import url, patterns

from .views import API

urlpatterns = patterns('',
    url(r'^api/', API.as_view(), name='api'),
)
