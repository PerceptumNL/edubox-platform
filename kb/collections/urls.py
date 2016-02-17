from django.conf.urls import url, include

from .views import learning_units

urlpatterns = [
    url(r'^learning-units/?$', learning_units, name='learning_units')
]
