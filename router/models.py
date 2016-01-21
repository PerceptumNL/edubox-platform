from django.db import models
from django.conf import settings

class ServerCookie(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=2049)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    domain = models.CharField(max_length=255)
