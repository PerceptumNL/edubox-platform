from django.db import models

class Question(models.Model):
    user = models.ForeignKey('kb.UserProfile')
    question = models.TextField()
    location = models.CharField(max_length=2000)
    answer = models.TextField()
    final_answer = models.BooleanField(default=False)
    answered = models.BooleanField(default=False)

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
