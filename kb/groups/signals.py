from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from .models import *
from kb.permissions.models import Permission
from kb.settings.models import UserDefault, GroupDefault


#Flat permissions computed based on changes in groups a user belongs to or
#roles in that group. 

@receiver(post_save)
def permissions_group_save(sender, **kwargs):
    if sender == Membership:
        #If a user is added to a group, those permission can be added to the user.
        if kwargs['created']:
            kwargs['instance'].user.flat_permissions.add(*(
                    kwargs['instance'].group.permissions.all() |
                    kwargs['instance'].role.permissions.all()))
        else:
            kwargs['instance'].user._recompute_flat_permissions()

@receiver(post_delete)
def permissions_group_delete(sender, **kwargs):
    if sender == Membership:
        kwargs['instance'].user._recompute_flat_permissions()

#Flat permissions computed based on changes in user, group or role permissions.

@receiver(m2m_changed)
def update_flat_permissions(sender, **kwargs):
    if kwargs['model'] == Permission:
        source = type(kwargs['instance'])
        if  (source == Group or source == Role):
            kwargs['instance']._update_flat_permissions(kwargs['action'],
                    kwargs['pk_set'])
        #User permissions require app context, so are not included
        #elif (source == UserProfile and sender == Context):

#Computing compact settings strings based on user or group defaults

@receiver(post_save)
def user_setting_strings(sender, **kwargs):
    if sender == UserDefault:
        app = kwargs['instance'].setting.app
        if app != None:
            kwargs['instance'].user._update_setting_string(app,
                    kwargs['instance'].group)

@receiver(post_save)
def group_setting_strings(sender, **kwargs):
    if sender == GroupDefault:
        app = kwargs['instance'].setting.app
        if app != None:
            group = kwargs['instance'].group
            for user in kwargs['instance'].group.users:
                user._update_setting_string(app, group)

"""
@receiver(m2m_changed)
def user_default_check(sender, **kwargs):
    if sender == UserDefault and kwargs['action'] == 'pre_add':
        for pk in pk_set:
            UserDefault.objects.filter(user=kwargs['instance'], 
                    settingVal=SettingValue.get(pk=pk)).delete()
"""
