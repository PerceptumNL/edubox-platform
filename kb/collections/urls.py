from django.conf.urls import url, include

from .views import learning_units, challenges, challenge_detail, list_all

urlpatterns = [
    url(r'^all/?$', list_all, name='collections_all'),
    url(r'^units/?$', learning_units, name='collections_learning_units'),
    url(r'^challenges/?$', challenges, name='collections_challenges'),
    url(r'^challenges/(?P<challenge_id>[^/]+)/?$', challenge_detail,
        name='collections_challenge_detail')
]
