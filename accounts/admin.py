from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import AppAccount

class InstituteFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'institute'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'institute'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        from kb.groups.models import Institute
        return Institute.objects.all().values_list('pk','title')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(profile__institute__pk=self.value())


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

    list_filter = ('is_staff', 'is_superuser', InstituteFilter)

    def institute(self, instance):
        return instance.profile.institute
    institute.short_name = "Institute"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(AppAccount)
