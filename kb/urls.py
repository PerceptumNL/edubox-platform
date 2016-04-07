from django.conf.urls import url, patterns, include

from .apps.views import app_list
from .inbox.views import message_list
from .csrf.views import get_csrf
from .questions.views import ask_question
from .skills.views import get_skills
from .events.views import API


urlpatterns = patterns('',
    url(r'^csrf/?', get_csrf),
    url(r'^apps/?', app_list),
    url(r'^inbox/?', message_list),
    url(r'^groups/?', include('kb.groups.urls')),
    url(r'^skills/?', get_skills, name='get_skills'),
    url(r'^events/', API.as_view()),
    url(r'^settings/', include('kb.settings.urls')),
    url(r'^collections/', include('kb.collections.urls')),
    url(r'^questions/', ask_question),
    url(r'^lvs/', include('kb.lvs.urls')),
)
