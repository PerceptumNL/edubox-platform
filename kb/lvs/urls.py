from django.conf.urls import url, patterns, include

from .views import upload_edexml, add_student

urlpatterns = patterns('',
    url(r'^student', add_student),
    url(r'^$', upload_edexml),
)
