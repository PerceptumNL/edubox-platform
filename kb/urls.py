from django.conf.urls import url, patterns, include

from .apps.views import app_list
from .csrf.views import get_csrf
from .events.views import API
from .inbox.views import message_list
from .releases.views import release_list
from .skills.views import get_skills
from .questions.views import ask_question


urlpatterns = patterns('',
    url(r'^apps/?', app_list),
    url(r'^collections/', include('kb.collections.urls')),
    url(r'^csrf/?', get_csrf),
    url(r'^events/', API.as_view()),
    url(r'^groups/?', include('kb.groups.urls')),
    url(r'^inbox/?', message_list),
    url(r'^lvs/', include('kb.lvs.urls')),
    url(r'^releases/?', release_list),
    url(r'^settings/', include('kb.settings.urls')),
    url(r'^skills/?', get_skills, name='get_skills'),
    url(r'^questions/', ask_question),
)
