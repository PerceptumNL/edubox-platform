from django.db import models
from django.utils import timezone

class Question(models.Model):
    user = models.ForeignKey('kb.UserProfile')
    question = models.TextField()
    browser_location = models.CharField(max_length=2000, default='', blank=True)
    location = models.CharField(max_length=2000)
    user_agent = models.CharField(max_length=255, default='unknown')
    answer = models.TextField()
    final_answer = models.BooleanField(default=False)
    answered = models.BooleanField(default=False)
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-datetime',)

    def __str__(self):
        return self.question[:20]

    def save(self, *args, **kwargs):
        if self.final_answer and not self.answered:
            from kb.inbox.models import Message
            Message.objects.create(
                user=self.user,
                title="Antwoord op: "+self.question[:200],
                body=self.answer)
            self.answered = True
        super().save(*args, **kwargs)
