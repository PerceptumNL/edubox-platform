from django.conf.urls import include, url

from .views import *

urlpatterns = [
    url(r'^sim1', sim1, name="router_sim1"),
]
