from django.conf.urls import patterns, include, url
from django.contrib import admin

from . import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.article_overview, name='article_overview'),
    url(r'update/?$',
        views.update_feeds, name='update_feeds'),
    url(r'articles/(?P<identifier>\d+)$',
        views.article, name='article'),
    url(r'categories/(?P<identifier>\d+)$',
        views.category, name='category'),
    url(r'query/?$', views.query, name='content_query'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^summernote/', include('django_summernote.urls')),
)
