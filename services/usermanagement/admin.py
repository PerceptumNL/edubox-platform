from django.contrib import admin
from .models import *

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
admin.site.register(Setting)
admin.site.register(SettingValue)
