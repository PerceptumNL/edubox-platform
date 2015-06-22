from django.db import models
from django.conf import settings

class Setting(models.Model):
    label = models.CharField(max_length=255)
    description = models.TextField()
    compact = models.BooleanField(default=True)
    
    app = models.ForeignKey('loader.App', null=True)

    def __str__(self):
        return self.label

    def __repr__(self):
        return "Setting(%s)" % (self,)

class SettingValue(models.Model):
    value = models.CharField(max_length=255)
    
    setting = models.ForeignKey(Setting)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
        related_name='settings')

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return "Value(%s)" % (self,)
