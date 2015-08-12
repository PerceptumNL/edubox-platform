from django.contrib import admin
from .models import Setting, SettingValue

admin.site.register(Setting)
admin.site.register(SettingValue)
