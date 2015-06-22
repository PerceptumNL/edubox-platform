from django.db import models
from django.conf import settings

class Setting(models.Model):
    label = models.CharField(max_length=255)
    description = models.TextField()
    
    app = models.ForeignKey('loader.App', null=True)

class SettingValue(models.Model):
    value = models.CharField(max_length=255)
    
    setting = models.ForeignKey(Setting)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
        related_name='settings')
