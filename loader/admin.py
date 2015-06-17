from django.contrib import admin
from .models import App

class AppAdmin(admin.ModelAdmin):
    list_display = ('title', 'local', 'root')

admin.site.register(App, AppAdmin)
