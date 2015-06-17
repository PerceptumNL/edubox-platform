from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

class App(models.Model):
    # Title of the application
    title = models.CharField(max_length=255)
    # Link to the application icon
    icon = models.URLField(null=True, blank=True)
    # Whether the app is hosted on the same domain or not
    local = models.BooleanField(default=True)
    # URL or urlconf where app can be found
    location = models.CharField(max_length=255)
    # The users of this application
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
            related_name="apps")

    @property
    def load_url(self):
        return reverse('app_routing', args=(self.pk,))

    def __unicode__(self):
        return unicode(self.title)

    def __repr__(self):
        return "App(%s)" % (str(self),)
