from django.conf.urls import url

from . import views

urlpatterns = patterns('',
    url(r'^post/', views.post_events, name='post_events'),
    url(r'^get/', views.get_events, name='get_events'),
)
