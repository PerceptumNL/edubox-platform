from django.db import models

from kb.apps.models import App

class Permission(models.Model):
    code = models.CharField(max_length=31, primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "permissions"

    def __str__(self):
        return self.name

class UserPermission(models.Model):
    user = models.ForeignKey('kb.UserProfile')
    permission = models.ForeignKey(Permission)

    app = models.ForeignKey(App)

    class Meta:
        app_label = "permissions"

    def __str__(self):
        return str(self.user) +' in '+ str(self.app) +' can '+ str(self.permission) 
