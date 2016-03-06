from django.conf.urls import url, patterns, include

from .views import group_list, group_details


urlpatterns = patterns('',
    url(r'^(?P<group_id>[0-9]+)/?', group_details),
    url(r'^$', group_list),
)
