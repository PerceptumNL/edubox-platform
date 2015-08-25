from django.contrib import admin
from .models import UserProfile, Group, Institute, Role
from .models import Permission, Setting, SettingValue, CompactSettings

admin.site.register(UserProfile)
admin.site.register(Group)
admin.site.register(Institute)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(Setting)
admin.site.register(SettingValue)
admin.site.register(CompactSettings)
