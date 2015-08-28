from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import *

class SettingAdmin(admin.ModelAdmin):
    list_display = ['code', 'app', 'description', 'group_default',
            'group_restrictions', 'user_preference']

    def group_default(self, obj):
        if not obj.single: 
            return ''
        link = reverse('group_defaults', args=[obj.pk])
        return '<a href="'+link+'">Edit settings</a>'
    
    def group_restrictions(self, obj):
        link = reverse('group_restrictions', args=[obj.pk])
        return '<a href="'+link+'">Edit settings</a>'
    
    def user_preference(self, obj):
        if obj.single:
            link = reverse('user_defaults', args=[obj.pk])
        else:
            link = reverse('user_restrictions', args=[obj.pk])
        return '<a href="'+link+'">Edit settings</a>'

    group_default.allow_tags = True
    group_restrictions.allow_tags = True
    user_preference.allow_tags = True
    group_default.short_description = 'Group Default'
    group_restrictions.short_description = 'Group Restrictions'
    user_preference.short_description = 'User Preference'

class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 1

class UserProfileAdmin(admin.ModelAdmin):
    inlines = [MembershipInline]
    exclude = ['flat_permissions']


class CompactSettingsInline(admin.TabularInline):
    model = CompactSettings
    extra = 1
    readonly_fields = ('string', 'user', 'group', 'app')

class UserPermissionsInline(admin.StackedInline):
    model = UserPermission
    extra = 1

class UserRestrictionsInline(admin.StackedInline):
    model = UserRestriction
    extra = 1

class UserDefaultsInline(admin.StackedInline):
    model = UserDefault
    extra = 1

class UserProfileProxyAdmin(UserProfileAdmin):
    inlines = [MembershipInline, UserPermissionsInline, UserRestrictionsInline,
            UserDefaultsInline, CompactSettingsInline]
    readonly_fields = ['flat_permissions']

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserProfileProxy, UserProfileProxyAdmin)
admin.site.register(Group)
admin.site.register(Institute)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(Setting, SettingAdmin)
admin.site.register(SettingValue)

admin.site.register(GroupRestriction)
