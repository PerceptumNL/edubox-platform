from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

@receiver(post_save)
def user_setting_strings(sender, **kwargs):
    app = kwargs['instance'].setting.app
    if sender == UserDefault and app != None:
        kwargs['instance'].user._update_setting_string(app,
                kwargs['instance'].group)

@receiver(post_save)
def group_setting_strings(sender, **kwargs):
    app = kwargs['instance'].setting.app
    if sender == GroupDefault and app != None:
        group = kwargs['instance'].group
        for user in kwargs['instance'].group.users:
            user._update_setting_string(app, group)

@receiver(m2m_changed)
def update_flat_permissions(sender, **kwargs):
    if kwargs['model'] == Permission:
        source = type(kwargs['instance'])
        #UserProfile had 2 ManyToMany's with Permission, distinguished by Context 
        if (source == UserProfile and sender == Context) or
                source == Group or source == Role:
            kwargs['instance']._update_flat_permissions(kwargs['action'],
                    kwargs['pk_set'])


#Can't be done using signals, because it requires all through object parameters
#in order to properly filter what elements to delete.
"""
@receiver(m2m_changed)
def user_default_check(sender, **kwargs):
    if sender == UserDefault and kwargs['action'] == 'pre_add':
        for pk in pk_set:
            UserDefault.objects.filter(user=kwargs['instance'], 
                    settingVal=SettingValue.get(pk=pk)).delete()
"""
