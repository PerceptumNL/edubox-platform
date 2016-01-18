from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

class App(models.Model):
    """
    Class for resources serving an Application.
    """
    root = models.CharField(max_length=255,
            verbose_name="URL/URLconf")
    # Regex matching all URL's that are considered to match root.
    identical_urls = models.CharField(blank=True, max_length=255)
    # Whether the remote root needs HTTPS
    secure = models.BooleanField(default=True)
    
    # Title of the application
    title = models.CharField(max_length=255)
    # Description of the applicaiont
    description = models.TextField()
    # Link to the application icon
    icon = models.URLField(null=True, blank=True)

    class Meta:
        app_label = "apps"

    @property
    def scheme(self):
        return 'https' if self.secure else 'http'

    @property
    def load_url(self):
        return reverse('app_routing', args=(self.pk, '/'))

    def __str__(self):
        return self.title

    def __repr__(self):
        return "App(%s)" % (self,)

