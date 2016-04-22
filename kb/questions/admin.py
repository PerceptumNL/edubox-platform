from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Question

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
            return queryset.filter(user__institute__pk=self.value())


class QuestionAdmin(SummernoteModelAdmin):
    model = Question
    search_fields = (
        'user__user__username',
        'user__user__email',
        'user__alias',
        'user__user__last_name',
        'user__user__first_name',
        'user__institute__title')
    list_display = ('short_question', 'full_user_description', 'location',
                    'datetime', 'final_answer')
    list_filter = ('final_answer', InstituteFilter)
    list_display_links = ('short_question',)

    def full_location(self, instance):
        from django.conf import settings
        return "<a href='%(domain)s#%(location)s'>%(location)s</a>" % {
                'domain': settings.FRONTEND_URL,
                'location': instance.location }
    full_location.allow_tags = True

    def full_browser_location(self, instance):
        from django.conf import settings
        if instance.browser_location:
            return "<a href='%(location)s'>%(location)s</a>" % {
                    'location': instance.browser_location }
        else:
            return "Browser was not used during this question."
    full_browser_location.allow_tags = True

    def full_user_description(self, instance):
        return "%(full_name)s of %(institute)s (%(username)s)" % {
                'full_name': instance.user.full_name,
                'institute': instance.user.institute,
                'username': instance.user.user.username }
    full_user_description.short_description = "User"

    def short_question(self, instance):
        if len(instance.question) > 50:
            return instance.question[:50]+"..."
        else:
            return instance.question

    def get_fields(self, request, obj=None):
        if obj is None:
            return ('user', 'datetime', 'location', 'browser_location',
                    'question')
        else:
            return  ('answered', 'full_user_description', 'datetime',
                     'user_agent', 'full_location', 'full_browser_location',
                     'question', 'answer', 'final_answer')

    def get_readonly_fields(self, request, obj=None):
        fields = ('answered',)
        if obj is not None:
            fields += ('full_user_description', 'question', 'datetime',
                      'full_location', 'full_browser_location', 'user_agent')
            if obj.final_answer:
                fields += ('answer',)
        return fields

admin.site.register(Question, QuestionAdmin)
