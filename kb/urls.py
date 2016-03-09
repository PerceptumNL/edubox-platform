from django.conf.urls import url, patterns, include

from .apps.views import app_list
from .lvs.views import upload_edexml
from .events.views import API


urlpatterns = patterns('',
    url(r'^apps/?', app_list),
    url(r'^groups/?', include('kb.groups.urls')),
    url(r'^events/', API.as_view()),
    url(r'^settings/', include('kb.settings.urls')),
    url(r'^collections/', include('kb.collections.urls')),
    url(r'^lvs/', upload_edexml),
)
