from django.conf.urls import include, url

from .views import login_user_into_app

urlpatterns = [
    url(r'apps/login/?', login_user_into_app, name="app_login"),
    url(r'', include('allauth.urls')),
]
