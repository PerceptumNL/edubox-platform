from django.conf.urls import url

from .views import API

urlpatterns = patterns('',
    url(r'^api/', API.as_view(), name='api'),
)
