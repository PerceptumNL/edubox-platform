from django.db import models
from django.conf import settings
from kb.apps.models import App

class AppAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    app = models.ForeignKey(App, related_name='+')
    username = models.CharField(max_length=255) #TODO: Encrypt
    password = models.CharField(max_length=255) #TODO: Encrypt
    params = models.TextField(default="{}", blank=True)

    class Meta:
        app_label = "accounts"
        verbose_name_plural = "app accounts"

    def __str__(self):
        return "Credentials of %s for %s" % (self.user, self.app)

    @property
    def parameters(self):
        from json import loads
        try:
            parameters = loads(self.params)
        except (ValueError, TypeError):
            return {}
        else:
            return parameters

    @classmethod
    def generate(cls, app, user, invalid_usernames=None):
        """Generate account credentials for user."""
        from strgen import StringGenerator
        invalid_usernames = invalid_usernames or []
        username = user.username
        for c in ['@', ':', '/']:
            username = username.replace(c, ".")
        base_username = username
        unique_counter = 1
        while username in invalid_usernames:
            username = "%s_%d" % (base_username, unique_counter)
            unique_counter += 1
        password = StringGenerator("[\w\d]{20}").render()
        return cls(user=user, app=app, username=username, password=password)
