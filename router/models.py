from django.db import models
from django.conf import settings
from kb.apps.models import App

class ServerCookiejar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    contents = models.BinaryField()
    """Used for pickled cookiejars."""

    class Meta:
        app_label = "router"


class ServerCredentials(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    app = models.ForeignKey(App, related_name='+')
    username = models.CharField(max_length=255) #TODO: Encrypt
    password = models.CharField(max_length=255) #TODO: Encrypt

    class Meta:
        app_label = "router"
        verbose_name_plural = "server credentials"
