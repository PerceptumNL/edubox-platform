from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'is_teacher', 'institute')
    list_filter = ('institute', 'is_teacher')
    search_fields = (
        'user__username',
        'user__email',
        'alias',
        'user__last_name',
        'user__first_name',
        'institute__title')

admin.site.register(UserProfile, UserProfileAdmin)
