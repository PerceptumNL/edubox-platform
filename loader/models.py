from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

class LocalOrRemoteResource(models.Model):
    """
    Class for local or remote resources.
    """
    root = models.CharField(max_length=255,
            verbose_name="URL/URLconf")
    # Whether the resource is hosted on the same domain or not
    local = models.BooleanField(default=True)
    # Regex matching all URL's that are considered to match root.
    identical_urls = models.CharField(null=True, blank=True, max_length=255)
    # Whether the remote root needs HTTPS
    secure = models.BooleanField(default=True)

    class Meta:
        abstract=True

    @property
    def scheme(self):
        return 'https' if self.secure else 'http'

class App(LocalOrRemoteResource):
    """
    Class for resources serving an Application.
    """
    # Title of the application
    title = models.CharField(max_length=255)
    # Link to the application icon
    icon = models.URLField(null=True, blank=True)
    # The users of this application
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
            related_name="apps")

    @property
    def load_url(self):
        return reverse('app_routing', args=(self.pk, '/'))

    def __str__(self):
        return self.title

    def __repr__(self):
        return "App(%s)" % (self,)

class Service(LocalOrRemoteResource):
    """
    Class for resources serving a Service.
    """
    # Unique identifier
    name = models.CharField(max_length=255, primary_key=True)
    # Title of the application
    title = models.CharField(max_length=255)

    @property
    def load_url(self):
        return reverse('service_routing', args=(self.pk, '/'))

    def __str__(self):
        return self.title

    def __repr__(self):
        return "Service(%s)" % (self,)
