from django.conf.urls import url, include

from .views import learning_units, challenges, challenge_detail

urlpatterns = [
    url(r'^units/?$', learning_units, name='learning_units'),
    url(r'^challenges/?$', challenges, name='challenges'),
    url(r'^challenges/(?P<challenge_id>[^/]+)/?$', challenge_detail,
        name='challenge_detail')
]
