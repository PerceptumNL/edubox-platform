from django.contrib import admin
from .models import *

class MembershipInline(admin.TabularInline):
    model = Membership

class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'institute')
    list_filter = ('institute',)
    inlines = [MembershipInline,]


admin.site.register(Group, GroupAdmin)
admin.site.register(Institute)
admin.site.register(Role)
admin.site.register(Membership)
