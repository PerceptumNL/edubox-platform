from django.db import models
from django.conf import settings

from kb.groups.models import *
from kb.settings.models import *
from kb.permissions.models import *

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True)

    #EdeXML additions
    alias = models.CharField(max_length=255, unique=True)
    surname_prefixes = models.CharField(max_length=127, blank=True)
    initials = models.CharField(max_length=15, blank=True)
    gender = models.PositiveSmallIntegerField(default=0)
    date_of_birth = models.DateField(blank=True)

    #Member specifies the role the user has in the group
    groups = models.ManyToManyField(Group, through=Membership, 
            through_fields=('user', 'group'), related_name='users')
    institute = models.ForeignKey(Institute, related_name='users')

    #User specific additions to permissions, outside of group or role
    #permission. UserPermissions specifies the app for which this addition applies
    permissions = models.ManyToManyField(Permission, through=UserPermission,
            through_fields=('user', 'permission'))
    #A list of all permissions a user has, computed from the user's group(s),
    #role(s) and user permissions. Should never be updated directly!
    flat_permissions = models.ManyToManyField(Permission, related_name='+')

    #Iff a Setting has default==null: the user may further restrict the
    #collection for that setting. Else: He must choice a default value.
    setting_restrictions = models.ManyToManyField(SettingValue,
            through=UserRestriction, through_fields=('user', 'settingVal'),
            related_name='user_restrictions')
    setting_defaults = models.ManyToManyField(SettingValue,
            through=UserDefault, through_fields=('user', 'settingVal'),
            related_name='user_defaults')

    class Meta:
        app_label = "kb"

    @property
    def username(self):
        return self.user.username
    
    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name
    
    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        full = self.first_name +' '
        
        if self.prefixes != '':
            full += self.prexfixes
        
        full += self.last_name
        return full
    
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
        for code, value in settings.iteritems():
            if value == None:
                value = Setting.objects.get(app=app, code=code).default.value
            settings_string += '&'+ code +'='+ value

        #Set the value in the corresonding CompactSettings, remove the first '&'
        compact, c = CompactSettings.objects.get_or_create(user=self,
                group=group, app=app)
        compact.string = settings_string[1:]
        compact.save()

    def _update_flat_permissions(self, action, pk_set):
        if action == 'post_add':
            self.flat_permissions.add(Permission.objects.in_bulk(pk_set).values())
        elif action == 'post_remove':
            self.flat_permissions.remove(Permission.objects.in_bulk(pk_set).values())
        elif action == 'post_clear':
            self.flat_permissions.clear()

    def _recompute_flat_permissions(self):
        self.flat_permissions.clear()
        for member in Membership.objects.filter(user=self):
            self.flat_permissions.add(*(member.group.permissions.all() |
                    member.role.permissions.all()))
        #User permissions require app context
        #self.flat_permissions.add(*self.permissions.all())

