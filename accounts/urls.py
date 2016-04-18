from django.conf.urls import include, url

from .views import login_user_into_app, get_user_info, redirect_password_change

urlpatterns = [
    url(r'apps/login/?', login_user_into_app, name="app_login"),
    url(r'info/?', get_user_info, name='user_info'),
    url(r'password/change/$', redirect_password_change,
        name="account_change_password"),
    url(r'', include('allauth.urls')),
]
