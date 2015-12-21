from django.db import models

from kb.apps.models import App

class Setting(models.Model):
    code = models.CharField(max_length=31, primary_key=True)
    description = models.TextField()

    #Default Value for this Setting. Iff null: the setting should resolve to
    #a collection of values instead of a single choice.
    default = models.OneToOneField('SettingValue', blank=True, null=True,
            related_name='+')

    #Indicates if the setting is simple enough to add to the request query dict
    #TODO: Reconsider the way this is implemented in loader.views._local_routing
    compact = models.BooleanField(default=True)

    #If compact: Setting must have a default (i.e. resolve to a single value)
    # -> Adding restrictions never updates the CompactSettings string.

    app = models.ForeignKey(App, blank=True, null=True)

    @property
    def single(self):
        return self.default != None

    def __str__(self):
        return self.code

    def __repr__(self):
        return "Setting(%s)" % (self,)


class SettingValue(models.Model):
    value = models.CharField(max_length=255)    
    setting = models.ForeignKey(Setting, related_name='values')

    def __str__(self):
        return self.value

    def __repr__(self):
        return "Value(%s)" % (self,)


class GroupRestriction(models.Model):
    group = models.ForeignKey('groups.Group')
    settingVal = models.ForeignKey(SettingValue)
    setting = models.ForeignKey(Setting)


class GroupDefault(models.Model):
    group = models.ForeignKey('groups.Group')
    settingVal = models.ForeignKey(SettingValue)
    setting = models.ForeignKey(Setting, related_name='group_defaults')


class UserRestriction(models.Model):
    user = models.ForeignKey('kb.UserProfile')
    settingVal = models.ForeignKey(SettingValue)
    setting = models.ForeignKey(Setting)
    #Group context is required to resolve the setting
    group = models.ForeignKey('groups.Group')


class UserDefault(models.Model):
    user = models.ForeignKey('kb.UserProfile')
    settingVal = models.ForeignKey(SettingValue)
    setting = models.ForeignKey(Setting, related_name='user_defaults')
    #Group context is required to resolve the setting
    group = models.ForeignKey('groups.Group', related_name='user_defaults')


class CompactSettings(models.Model):
    #The string containing all compact (added to the request) settings for the
    #user, computed from (group and user)'s restrictions and defaults
    string = models.CharField(max_length=511, default='')

    user = models.ForeignKey('kb.UserProfile', related_name='compact_settings')
    group = models.ForeignKey('groups.Group')
    app = models.ForeignKey(App)

    class Meta:
        verbose_name_plural = 'Compact settings'

