from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import AppAccount

class CustomUserAdmin(UserAdmin):
    search_fields = (
        'username',
        'email',
        'profile__alias',
        'last_name',
        'first_name',
        'profile__institute__title')
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'last_login', 'institute')

    list_filter = ('is_staff', 'is_superuser', 'profile__institute__brincode')

    def institute(self, instance):
        return instance.profile.institute
    institute.short_name = "Institute"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(AppAccount)
