from django.contrib import admin
from .models import *

class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'institute')
    list_filter = ('institute',)

admin.site.register(Group, GroupAdmin)
admin.site.register(Institute)
admin.site.register(Role)
admin.site.register(Membership)
