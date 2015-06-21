from django.conf.urls import include, url
from .views import handle

urlpatterns = [
    url(r'^$', handle, name='handle')
]
