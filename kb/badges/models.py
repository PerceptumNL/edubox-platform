from django.db import models

from kb.models import UserProfile

class Badge(models.Model):
    code = models.CharField(max_length=31, primary_key=True)
    description = models.TextField()
    
    start_level = models.ForeignKey('BadgeLevel')
    users = models.ManyToManyField(UserProfile, through='UserBadge')

    def update_badge(self, user, xp):
        user = UserProfile.objects.get(pk=user)
       
        instance = UserBadge.objects.get_or_create(user=user, badge=self)
        instance.xp += xp

        if instance.xp >= instance.level.xp_thres:
            instance.level = instance.level.next_level

    def __str__(self):
        return self.code

    def __repr__(self):
        return "Badge (%s)" % (self,)


class BadgeLevel(models.Model):
    level = models.CharField(max_length=31, primary_key=True)
    
    xp_thres = models.PositiveSmallIntegerField()
    next_level = models.ForeignKey('BadgeLevel', blank=True, null=True)

    def __str__(self):
        return self.level

    def __repr__(self):
        return "Badge Level (%s)" % (self,)


class UserBadge(models.Model):
    user = models.ForeignKey(UserProfile)
    badge = models.ForeignKey(Badge)
    
    level = models.ForeignKey(BadgeLevel)
    xp = models.PositiveSmallIntegerField()

    def __init__(self, user, badge):
        self.user = user
        self.badge = badge

        self.level = badge.start_level
        self.xp = 0

    def __str__(self):
        return self.user +' has '+ self.level + ' in ' + self.badge 

    def __repr__(self):
        return "User Badge (%s)" % (self,)

    
