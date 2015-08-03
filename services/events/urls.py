from django.conf.urls import url, include, patterns

from rest_framework import routers

from .views import API, ReadEventViewSet

router = routers.DefaultRouter()
router.register(r'read_events', ReadEventViewSet)


urlpatterns = patterns('',
    url(r'^api/', API.as_view(), name='api'),
    url(r'^rest/', include(router.urls)),
)
