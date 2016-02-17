from django.db import models
from django.contrib.postgres.fields import JSONField
from kb.models import UserProfile

class Task(models.Model):
    label = models.CharField(max_length=255)
    completed_by = models.ManyToManyField(UserProfile, through=TaskCompletion,
            related_name='completed_tasks')

class Observable(models.Model):
    task = models.ForeignKey(Task, related_name='observables')
    completed_by = models.ManyToManyField(UserProfile, through=Observation,
            related_name='observations')
    pattern = JSONField()

class TaskCompletion(models.Model):
    task = models.ForeignKey(Task)
    user = models.ForeignKey(UserProfile)
    datetime = models.DateTimeField(auto_now_add=True)

class Observation(models.Model):
    observable = models.ForeignKey(Observable)
    user = models.ForeignKey(UserProfile)
    event = models.ForeignKey(GenericEvent)
    task = models.ForeignKey(Task)
    datetime = models.DateTimeField(auto_now_add=True)
