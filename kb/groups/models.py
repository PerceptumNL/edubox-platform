from django.db import models

from .helpers import *

from kb.apps.models import App
from kb.settings.models import *
from kb.permissions.models import *
from kb.lvs.models import XmlDump

class Group(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True)

    apps = models.ManyToManyField(App)

    parent = models.ForeignKey('Group', blank=True, null=True,
            related_name='subgroups')
    institute = models.ForeignKey('Institute', related_name='groups')

    permissions = models.ManyToManyField(Permission, blank=True)

    setting_restrictions = models.ManyToManyField(SettingValue,
            through=GroupRestriction, 
            through_fields=('group', 'settingVal'),
            related_name='group_restrictions')
    setting_defaults = models.ManyToManyField(SettingValue,
            through=GroupDefault,
            through_fields=('group', 'settingVal'),
            related_name='group_defaults')

    tags = models.ManyToManyField('Tag', blank=True)
    imported = models.BooleanField(default=False)

    inactive = models.BooleanField(default=False)

    class Meta:
        app_label = "groups"

    def __str__(self):
        return self.title

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

    def _update_flat_permissions(self, action, pk_set):
        for user in self.users.all():
            user._update_flat_permissions(action, pk_set)
        for group in self.subgroups.all():
            group._update_flat_permissions(action, pk_set)


class Institute(models.Model):
    title = models.CharField(max_length=255)
    email_domain = models.CharField(max_length=255)
    brincode = models.CharField(max_length=10, blank=True, default='');
    #The apps an institute (client) has access to, OS-level setting
    apps = models.ManyToManyField(App)
    xmls = models.ManyToManyField(XmlDump, blank=True)

    class Meta:
        app_label = "groups"

    def __str__(self):
        return self.title

class Membership(models.Model):
    #TODO: Should this be a foreign key to User rather than UserProfile?
    #  (Membership.get(..).user.user seems a bit clunky)
    # Alternatively call it userprofile or profile
    user = models.ForeignKey('kb.UserProfile')
    group = models.ForeignKey(Group)

    role = models.ForeignKey('Role', related_name='members')

    class Meta:
        app_label = "groups"

    def __str__(self):
        return str(self.user) +' as '+ str(self.role) +' in '+ str(self.group)


class Role(models.Model):
    role = models.CharField(max_length=31)
    permissions = models.ManyToManyField(Permission)

    class Meta:
        app_label = "groups"

    def __str__(self):
        return self.role

    def _update_flat_permissions(self, action, pk_set):
        for member in self.members.all():
            member.user._update_flat_permissions(action, pk_set)

class Tag(models.Model):
    label = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.label

