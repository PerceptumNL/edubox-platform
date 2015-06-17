from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

class LocalOrRemoteResource(models.Model):
    root = models.CharField(max_length=255,
            verbose_name="URL/URLconf")

    class Meta:
        abstract=True

class App(LocalOrRemoteResource):
    # Title of the application
    title = models.CharField(max_length=255)
    # Link to the application icon
    icon = models.URLField(null=True, blank=True)
    # Whether the app is hosted on the same domain or not
    local = models.BooleanField(default=True)
    # The users of this application
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
            related_name="apps")

    @property
    def load_url(self):
        return reverse('app_routing', args=(self.pk, '/'))

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return "App(%s)" % (self,)

class Service(LocalOrRemoteResource):
    # Unique identifier
    name = models.CharField(max_length=255, primary_key=True)
    # Title of the application
    title = models.CharField(max_length=255)
    # Whether the app is hosted on the same domain or not
    local = models.BooleanField(default=True)

    @property
    def load_url(self):
        return reverse('service_routing', args=(self.pk, '/'))

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return "Service(%s)" % (self,)
