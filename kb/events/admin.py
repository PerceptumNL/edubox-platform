from django.contrib import admin

from .models import *

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
            return queryset.filter(user__profile__institute__pk=self.value())

class EventAdmin(admin.ModelAdmin):
    list_display = (
        'event_type', 'user', 'verb', 'obj', 'group',
        'institute', 'timestamp')
    list_filter = (InstituteFilter,)
    search_fields = (
        'user__username',
        'user__email',
        'user__profile__alias',
        'user__last_name',
        'user__first_name',
        'user__profile__institute__title')

    def institute(self, instance):
        return instance.user.profile.institute.title

    def event_type(self, instance):
        return instance.__class__.__name__

admin.site.register(Verb)
admin.site.register(GenericEvent)
admin.site.register(ReadEvent, EventAdmin)
admin.site.register(RatedEvent, EventAdmin)
admin.site.register(ScoredEvent, EventAdmin)
admin.site.register(ClickedEvent, EventAdmin)
admin.site.register(SubmittedEvent, EventAdmin)
