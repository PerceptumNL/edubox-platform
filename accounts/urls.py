from django.conf.urls import include, url

from .views import login_user_into_app, get_user_info

urlpatterns = [
    url(r'apps/login/?', login_user_into_app, name="app_login"),
    url(r'info/?', get_user_info, name='user_info'),
    url(r'', include('allauth.urls')),
]
