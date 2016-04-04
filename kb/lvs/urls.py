from django.conf.urls import url, patterns, include

from .views import *

urlpatterns = patterns('',
    url(r'^upload$', upload_edexml),
    url(r'^process$', process_institute),
    url(r'^process/2$', process_teachers),
    url(r'^process/3$', process_groups),
    url(r'^student$', add_student),
)
