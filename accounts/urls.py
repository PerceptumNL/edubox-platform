from django.conf.urls import include, url

from .views import login_user_into_app, get_user_info, change_password

urlpatterns = [
    url(r'apps/login/?', login_user_into_app, name="app_login"),
    url(r'info/?', get_user_info, name='user_info'),
    url(r'change_password/?', change_password, name='change_password'),
    url(r'', include('allauth.urls')),
]
