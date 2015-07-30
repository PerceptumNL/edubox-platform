from django.db import models
from django.contrib.auth.models import User
#from django.contrib.sites.models import Site
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.signals import request_started
from django.dispatch import receiver

import pytz

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    groups = models.ManyToManyField('Group', blank=True, related_name='users')
    institute = models.ForeignKey('Institute', blank=True, null=True,
            related_name='users')

    def __unicode__(self):
        return unicode(self.user)

    def __str__(self):
        return unicode(self).encode('utf-8')

    @property
    def is_teacher(self):
        return Group.objects.filter(leader=self.user).exists()

class Group(models.Model):
    title = models.CharField(max_length=255)
    leader = models.ForeignKey(User, null=True, blank=True, related_name='teaches')
    institute = models.ForeignKey('Institute', null=True, blank=True)
    code = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return u'Group "%s" of %s' % (self.title, self.leader)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def pk_hash(self):
        pk_code = "%03d" % (self.pk*17,)
        pk_code = pk_code[-3:]
        return pk_code

    def generate_new_code(self):
        done=False
        code = ""
        while not done:
            pkcode = self.pk_hash()
            groupcode = generate_password('-')
            code = "%s-%s" % (pkcode, groupcode)
            grouplist = Group.objects.filter(code=code)
            if not grouplist:
                done=True
        return code

    def save(self, *args, **kwargs):
        if not self.code:
            if not self.pk:
                super(Group, self).save(*args, **kwargs)
            self.code = self.generate_new_code()
        super(Group, self).save()

class Institute(models.Model):
    title = models.CharField(max_length=255)
    #site_id = models.ForeignKey(Site)
    timezone = models.CharField(max_length=100,
            choices=zip(pytz.common_timezones, pytz.common_timezones))

    """
    @staticmethod
    @receiver(request_started)
    def set_current_timezone(*args, **kwargs):
        try:
            institute = Institute.objects.get(
                    site_id=Site.objects.get_current())
        except Institute.DoesNotExist:
            pass
        else:
            timezone.activate(institute.timezone)
    """

    def __repr__(self):
        return '%s' % (self.title)

    def __unicode__(self):
        return unicode(self.title)


