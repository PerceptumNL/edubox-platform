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
            through='UserRestriction', through_fields=('user', 'settingVal'),
            related_name='user_restrictions')
    setting_defaults = models.ManyToManyField('SettingValue',
            through='UserDefault', through_fields=('user', 'settingVal'),
            related_name='user_defaults')
    
    def __str__(self):
        return str(self.user)

    def _update_setting_string(self, app, group):
        settings = {setting.code: None for setting in
                Settings.objects.filter(compact=True, app=app)}
        settings_string = ''
        #Force QuerySet evaltion so the database is only hit once for user defaults
        user_settings = list(UserDefault.objects.filter(user=self, setting__app=app))

        while group != None:
            #Apply user defaults for this group context
            for default in user_settings.filter(group=group):
                code = default.setting.code
                if code in settings:
                    settings_string += '&'+ code +'='+ default.settingVal.value
                    #Remove the setting from dict, so new value cannot be set
                    settings.pop(code)
            
            #Find group-level defaults for setttings that have not been set yet
            for default in GroupDefault.objects.filter(group=group, setting__app=app):
                code = default.setting.code
                if code in settings and settings[code] == None:
                    settings[code] = default.settingVal.value
            
            #Move up to next group in the hierarchy
            group = group.parent
        
        #Add all group defaults that had no user defaults
        for setting, value in settings.iteritems():
            settings_string += '&'+ code +'='+ value

        #Set the value in the corresonding CompactSettings, remove the first '&'
        compact, c = CompactSettings.objects.get_or_create(user=self,
                group=group, app=app)
        compact.string = settings_string[1:]
        compact.save()

    def _update_flat_permissions(self, action, pk_set):
        if action == 'post_add':
            self.flat_permissions.add([Permission.objects.get(pk) for pk in pk_set])
        elif action == 'post_remove':
            self.flat_permissions.remove([Permission.objects.get(pk) for pk in pk_set])
        elif action == 'post_clear':
            self.flat_permissions.clear()

class Group(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True)
    
    apps = models.ManyToManyField(App, blank=True, null=True)

    parent = models.ForeignKey('Group', blank=True, null=True,
            related_name='subgroups')
    institute = models.ForeignKey('Institute', related_name='groups')

    permissions = models.ManyToManyField('Permission')

    setting_restrictions = models.ManyToManyField('SettingValue',
            through='GroupRestriction', through_fields=('group', 'settingVal'),
            related_name='group_restrictions')
    setting_defaults = models.ManyToManyField('SettingValue',
            through='GroupDefault', through_fields=('group', 'settingVal'),
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

    def _update_flat_permissions(self, action, pk_set):
        for user in self.users:
            user._update_flat_permissions(action, pk_set)
        for group in self.subgroups:
            group._update_flat_permissions(action, pk_set)
        
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

    role = models.ForeignKey('Role', related_name='members')

    def __str__(self):
        return str(self.user) +' as '+ str(self.role) +' in '+ str(self.group)

class Role(models.Model):
    role = models.CharField(max_length=31)
    
    permissions = models.ManyToManyField('Permission')

    def __str__(self):
        return dict(options)[self.role]

    def _update_flat_permissions(self, action, pk_set):
        for member in self.members:
            member.user._update_flat_permissions(action, pk_set)

#Through models for Permissions and Settings

class Context(models.Model):
    user = models.ForeignKey('UserProfile')
    permission = models.ForeignKey('Permission')

    app = models.ForeignKey(App)

    def __str__(self):
        return str(self.user) +' in '+ str(self.app) +' can '+ str(self.permission) 

class GroupRestriction(models.Model):
    group = models.ForeignKey('Group')
    settingVal = models.ForeignKey('SettingValue')
    
    setting = models.ForeignKey('Setting')


class GroupDefault(models.Model):
    group = models.ForeignKey('Group')
    settingVal = models.ForeignKey('SettingValue')
    
    setting = models.ForeignKey('Setting', related_name='group_defaults')

class UserRestriction(models.Model):
    user = models.ForeignKey('UserProfile')
    settingVal = models.ForeignKey('SettingValue')
    
    setting = models.ForeignKey('Setting')
    #Group context is required to resolve the setting
    group = models.ForeignKey('Group')

class UserDefault(models.Model):
    user = models.ForeignKey('UserProfile')
    settingVal = models.ForeignKey('SettingValue')
    
    setting = models.ForeignKey('Setting', related_name='user_defaults')
    #Group context is required to resolve the setting
    group = models.ForeignKey('Group', related_name='user_defaults')

#Permission and Setting models

class Permission(models.Model):
    code = models.CharField(max_length=31, primary_key=True)
    name = models.CharField(max_length=255)
   
    def __str__(self):
        return self.name

class Setting(models.Model):
    code = models.CharField(max_length=31, primary_key=True)
    description = models.TextField()
    
    #Default Value for this Setting. Iff null: the setting should resolve to
    #a collection of values instead of a single choice.
    default = models.OneToOneField('SettingValue', null=True, related_name='+')
    
    #Indicates if the setting is simple enough to add to the request query dict
    #TODO: Reconsider the way this is implemented in loader.views._local_routing
    compact = models.BooleanField(default=True)

    #If compact: Setting must have a default (i.e. resolve to a single value)
    # -> Adding restrictions never updates the CompactSettings string.

    app = models.ForeignKey(App, null=True)

    @property
    def single(self):
        return self.default != None

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

class CompactSettings(models.Model):
    #The string containing all compact (added to the request) settings for the
    #user, computed from (group and user)'s restrictions and defaults
    string = models.CharField(max_length=511, default='')

    user = models.ForeignKey('UserProfile', related_name='compact_settings')
    group = models.ForeignKey('Group')
    app = models.ForeignKey(App)


