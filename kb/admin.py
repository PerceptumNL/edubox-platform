from django.contrib import admin
from . import App

class AppAdmin(admin.ModelAdmin):
    list_display = ('title', 'root')

admin.site.register(App, AppAdmin)
