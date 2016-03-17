from django.db import models

from kb.models import UserProfile

class Badge(models.Model):
    T_SYSTEM_BADGE = 0
    T_SKILL_BADGE = 1

    BADGE_TYPES = ((0, 'System badge'), (1, 'Skill badge'))

    badge_id = models.CharField(max_length=31, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    badge_type = models.PositiveSmallIntegerField(choices=BADGE_TYPES,
            default=0)
    order = models.PositiveSmallIntegerField(default=0)

    start_level = models.ForeignKey('BadgeLevel')
    show_in_dashboard = models.BooleanField(default=True)
    users = models.ManyToManyField(UserProfile, through='UserBadge')

    def update_badge(self, user_or_id, xp):
        if not isinstance(user_or_id, UserProfile):
            user = UserProfile.objects.get(pk=user_or_id)
        else:
            user = user_or_id

        instance, _ = UserBadge.objects.get_or_create(user=user, badge=self)
        instance.xp += xp

        next_level = instance.level.next_level if instance.level else \
            self.start_level

        while next_level is not None and instance.xp >= next_level.xp_thres:
            instance.level = next_level
            next_level = instance.level.next_level

        instance.save()

    def __str__(self):
        return self.title

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, self)


class BadgeLevel(models.Model):
    level = models.CharField(max_length=31, primary_key=True)

    xp_thres = models.PositiveSmallIntegerField()
    next_level = models.ForeignKey('BadgeLevel', blank=True, null=True)
    index = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.level

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, self)


class UserBadge(models.Model):
    user = models.ForeignKey(UserProfile)
    badge = models.ForeignKey(Badge)

    level = models.ForeignKey(BadgeLevel, null=True, blank=True)
    xp = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "%s has %s (%d xp) in %s" % (self.user, self.level, self.xp, self.badge)

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, self)

