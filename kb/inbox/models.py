from django.db import models

class Message(models.Model):
    user = models.ForeignKey('kb.UserProfile')
    datetime = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
