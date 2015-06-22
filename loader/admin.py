from django.contrib import admin
from .models import App, Service

class AppAdmin(admin.ModelAdmin):
    list_display = ('title', 'local', 'root')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'local', 'root')

admin.site.register(App, AppAdmin)
admin.site.register(Service, ServiceAdmin)
