from django.db import models

class Question(models.Model):
    user = models.ForeignKey('kb.UserProfile')
    question = models.TextField()
    location = models.CharField(max_length=2000)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return self.question[:20]


class Answer(models.Model):
    question = models.ForeignKey('Question')
    answer = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.answer[:20]
