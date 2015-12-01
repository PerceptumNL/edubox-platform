from django.conf.urls import url, include, patterns

from .views import *

urlpatterns = patterns('',
    url(r'^(?P<setting_id>[^/]+)/(?P<setting_type>[^/]+)/(?P<value_id>[^/]+)', settings),
    ## Old endpoints (still needed in the admin)
    url(r'^(.+)/defaults/user/', user_defaults, name='user_restrictions'),
    url(r'^(.+)/defaults/group/', group_defaults, name='group_defaults'),
    url(r'^(.+)/restrictions/user/', user_restrictions, name='user_defaults'),
    url(r'^(.+)/restrictions/group/$', group_restrictions, name='group_restrictions'),
    url(r'^(.+)/restrictions/group/form_submit/', group_form),
    url(r'^(.+)/restrictions/group/(.+)/form_submit/$', restrict_form),
    url(r'^(.+)/restrictions/group/(.+)/$', group_restrictions_select,
            name='group_restrictions_select')
)
