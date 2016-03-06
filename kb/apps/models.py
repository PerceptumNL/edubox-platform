from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
import json

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
    # JSON serialization of login script configuration
    # (TODO: Change to JSONField)
    login_config_json = models.TextField(default="{}", blank=True)
    # App connector class for app-specific behaviour
    connector_class = models.CharField(default='', blank=True, max_length=255)

    class Meta:
        app_label = "apps"

    @property
    def scheme(self):
        return 'https' if self.secure else 'http'

    @property
    def load_url(self):
        return reverse('app_routing', args=(self.pk, '/'))

    @property
    def login_config(self):
        return json.loads(self.login_config_json)

    def __str__(self):
        return self.title

    def __repr__(self):
        return "App(%s)" % (self,)

