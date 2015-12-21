from django.contrib import admin
from .models import *

class AppAdmin(admin.ModelAdmin):
    list_display = ('title', 'root')

admin.site.register(App, AppAdmin)
