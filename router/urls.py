from django.conf.urls import include, url

from .views import *

urlpatterns = [
    url(r'^sim-login/(?P<app_id>[^/]+)/?', sim_login, name="router_sim_login"),
    url(r'^sim-signup/(?P<app_id>[^/]+)/?', sim_signup,
        name="router_sim_signup"),
]
