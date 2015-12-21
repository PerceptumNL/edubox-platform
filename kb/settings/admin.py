from django.contrib import admin
from .models import *

admin.site.register(Setting)
admin.site.register(SettingValue)

admin.site.register(GroupRestriction)
admin.site.register(GroupDefault)
admin.site.register(UserRestriction)
admin.site.register(UserDefault)
