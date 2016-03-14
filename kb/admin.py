from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'teacher', 'institute')
    list_filter = ('institute',)
    search_fields = (
        'user__username',
        'user__email',
        'alias',
        'user__last_name',
        'user__first_name',
        'institute__title')

    def teacher(self, instance):
        return instance.is_teacher()
    teacher.boolean = True

admin.site.register(UserProfile, UserProfileAdmin)
