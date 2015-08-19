from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from loader.models import App

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
   
    #Member specifies the role the user has in the group
    groups = models.ManyToManyField('Group', through='Member', 
            through_fields=('user', 'group'), related_name='users')
    institute = models.ForeignKey('Institute', related_name='users')
    
    #User specific additions to permissions, outside of group or role
    #permission. Context specifies the app for which this addition applies
    permissions = models.ManyToManyField('Permission', through='Context', 
            through_fields=('user', 'permission'))
    #A list of all permissions a user has, computed from the user's group(s),
    #role(s) and user permissions. Should never be updated directly!
    flat_permissions = models.ManyToManyField('Permission', related_name='+')
   
    #Iff a Setting has default==null: the user may further restrict the
    #collection for that setting. Else: He must choice a default value.
    setting_restrictions = models.ManyToManyField('SettingValue',
            related_name='user_restrictions')
    setting_defaults = models.ManyToManyField('SettingValue',
            related_name='user_defaults')
    #Flattened Settings where compact==True.
    setting_string = models.OneToOneField('SettingString', null=True)
    
    def __str__(self):
        return str(self.user)

class Group(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True)
    
    parent = models.ForeignKey('Group', blank=True, null=True,
            related_name='subgroups')
    institute = models.ForeignKey('Institute', related_name='groups')

    permissions = models.ManyToManyField('Permission')

    setting_restrictions = models.ManyToManyField('SettingValue',
            through='Restriction', through_fields=('group', 'settingVal'),
            related_name='group_restrictions')
    setting_defaults = models.ManyToManyField('SettingValue',
            through='Default', through_fields=('group', 'settingVal'),
            related_name='group_defaults')
    
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

class Institute(models.Model):
    title = models.CharField(max_length=255)
    #The apps an institute (client) has access to, OS-level setting
    apps = models.ManyToManyField(App)

    def __str__(self):
        return self.title

#Through models for Users and Groups

class Member(models.Model):
    user = models.ForeignKey('UserProfile')
    group = models.ForeignKey('Group')

    role = models.ForeignKey('Role')

    def __str__(self):
        return str(self.user) +' as '+ str(self.role) +' in '+ str(self.group)

class Role(models.Model):
    options = (('St', 'Student'),
            ('Te', 'Teacher'),
            ('Me', 'Mentor'),
            ('Ex', 'Executive'))
    role = models.CharField(max_length=2, choices=options)
    
    permissions = models.ManyToManyField('Permission')

    def __str__(self):
        return dict(options)[self.role]

#Through models for Permissions and Settings

class Context(models.Model):
    user = models.ForeignKey('UserProfile')
    permission = models.ForeignKey('Permission')

    app = models.ForeignKey(App)

    def __str__(self):
        return str(self.user) +' in '+ str(self.app) +' can '+ str(self.permission) 

class Restriction(models.Model):
    group = models.ForeignKey('Group')
    settingVal = models.ForeignKey('SettingValue')
    
    setting = models.ForeignKey('Setting')

class Default(models.Model):
    group = models.ForeignKey('Group')
    settingVal = models.ForeignKey('SettingValue')
    
    setting = models.ForeignKey('Setting', related_name='group_defaults')

#Permission and Setting models

class Permission(models.Model):
    code = models.CharField(max_length=31)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Setting(models.Model):
    label = models.CharField(max_length=31)
    valueType = models.CharField(max_length=15)
    description = models.TextField()
    
    #Default Value for this Setting. Iff null: the setting should resolve to
    #a collection of values instead of a slinge choice.
    default = models.OneToOneField('SettingValue', null=True, related_name='+')

    #Indicates if the setting is simple enough to add to the request query dict
    #TODO: Reconsider the way this is implemented in loader.views._local_routing
    compact = models.BooleanField(default=True)
    
    app = models.ForeignKey(App, null=True)

    def __str__(self):
        return self.label

    def __repr__(self):
        return "Setting(%s)" % (self,)

class SettingValue(models.Model):
    value = models.CharField(max_length=255)    
    setting = models.ForeignKey(Setting, related_name='values')

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return "Value(%s)" % (self,)

class SettingString(models.Model):
    #The string containing all compact (added to the request) settings for the
    #user, computed from (group and user)'s restrictions and defaults
    string = models.CharField(max_length=511)

