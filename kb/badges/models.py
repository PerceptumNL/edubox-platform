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

    start_level = models.ForeignKey('BadgeLevel')
    users = models.ManyToManyField(UserProfile, through='UserBadge')

    def update_badge(self, user_or_id, xp):
        if not isinstance(user_or_id, UserProfile):
            user = UserProfile.objects.get(pk=user_or_id)
        else:
            user = user_or_id

        instance, _ = UserBadge.objects.get_or_create(user=user, badge=self)
        instance.xp += xp

        while instance.xp >= instance.level.xp_thres and \
                instance.level.next_level is not None:
            instance.level = instance.level.next_level

        instance.save()

    def __str__(self):
        return self.title

    def __repr__(self):
        return "Badge (%s)" % (self,)


class BadgeLevel(models.Model):
    level = models.CharField(max_length=31, primary_key=True)

    xp_thres = models.PositiveSmallIntegerField()
    next_level = models.ForeignKey('BadgeLevel', blank=True, null=True)
    index = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.level

    def __repr__(self):
        return "Badge Level (%s)" % (self,)


class UserBadge(models.Model):
    user = models.ForeignKey(UserProfile)
    badge = models.ForeignKey(Badge)

    level = models.ForeignKey(BadgeLevel)
    xp = models.PositiveSmallIntegerField()

    def __init__(self, *args, **kwargs):
        if 'level' not in kwargs and 'badge' in kwargs:
            kwargs['level'] = kwargs['badge'].start_level
        if 'xp' not in kwargs:
            kwargs['xp'] = 0
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s has %s (%d xp) in %s" % (self.user, self.level, self.xp, self.badge)

    def __repr__(self):
        return "User Badge (%s)" % (self,)

