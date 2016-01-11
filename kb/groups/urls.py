from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^import/students/process/$', process_students),
    url(r'^import/students/$', student_form, name='student_form'),
    url(r'^import/teachers/process/$', process_teachers),
    url(r'^import/teachers/$', teacher_form, name='teacher_form'),
]

