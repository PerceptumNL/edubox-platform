from django.conf.urls import url, patterns

from .views import API

urlpatterns = patterns('',
    url(r'^events/', API.as_view()),
)
