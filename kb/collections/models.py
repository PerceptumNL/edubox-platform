from django.db import models
from django.contrib.postgres.fields import JSONField
from kb.models import UserProfile
from kb.events.models import GenericEvent
#TODO from kb.badges.models import Badge

class Activity(models.Model):
    label = models.CharField(max_length=255)
    completed_by = models.ManyToManyField(UserProfile,
            through='ActivityCompletion', related_name='completed_tasks')


class LearningUnit(models.Model):
    label = models.CharField(max_length=255)
    ordered = models.BooleanField(default=True)
    activities = models.ManyToManyField(Activity)
    #TODO dependencies = models.ManyToManyField(Badge)
    #TODO provides = models.ManyToManyField(Badge, through=LearningUnitOutcome)


class Collection(models.Model):
    label = models.CharField(max_length=255)
    author = models.ForeignKey(UserProfile)
    learning_units = models.ManyToManyField(LearningUnit)


#TODO
#class LearningUnitOutcome(models.Model):
#    learning_unit = models.ForeignKey(LearningUnit)
#    badge = models.ForeignKey(Badge)
#    xp = models.PositiveSmallIntegerField()


class Observable(models.Model):
    activity = models.ForeignKey(Activity, related_name='observables')
    completed_by = models.ManyToManyField(UserProfile, through='Observation',
            related_name='observations')
    pattern = JSONField()


class ActivityCompletion(models.Model):
    activity = models.ForeignKey(Activity)
    user = models.ForeignKey(UserProfile)
    datetime = models.DateTimeField(auto_now_add=True)


class Observation(models.Model):
    observable = models.ForeignKey(Observable)
    user = models.ForeignKey(UserProfile)
    event = models.ForeignKey(GenericEvent)
    activity = models.ForeignKey(Activity)
    datetime = models.DateTimeField(auto_now_add=True)
