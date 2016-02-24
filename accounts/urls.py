from django.conf.urls import include, url

from .views import login

urlpatterns = [
    url(r'^apps/login/', login, name="app_login"),
]
