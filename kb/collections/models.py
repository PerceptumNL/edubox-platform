from django.db import models
from django.contrib.postgres.fields import JSONField
from kb.models import UserProfile
from kb.apps.models import App
from kb.events.models import GenericEvent
#TODO from kb.badges.models import Badge

class Activity(models.Model):
    label = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    app = models.ForeignKey(App)
    completed_by = models.ManyToManyField(UserProfile,
            through='ActivityCompletion', related_name='completed_tasks')

    def __str__(self):
        return self.label


class LearningUnit(models.Model):
    label = models.CharField(max_length=255)
    activities = models.ManyToManyField(Activity, through='LearningUnitItem')
    order = models.PositiveSmallIntegerField(default=0)
    #TODO dependencies = models.ManyToManyField(Badge)
    #TODO provides = models.ManyToManyField(Badge, through=LearningUnitOutcome)

    def __str__(self):
        return self.label

    def get_next_activity_for_user(self, user):
        return self.activities.exclude(completed_by=user.profile).first()


class LearningUnitItem(models.Model):
    learning_unit = models.ForeignKey(LearningUnit)
    activity = models.ForeignKey(Activity)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('order',)


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

    def __str__(self):
        return "%s completed %s" % (self.user, self.activity)


class Observation(models.Model):
    observable = models.ForeignKey(Observable)
    user = models.ForeignKey(UserProfile)
    event = models.ForeignKey(GenericEvent)
    activity = models.ForeignKey(Activity)
    datetime = models.DateTimeField(auto_now_add=True)
