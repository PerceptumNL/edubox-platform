from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Question

class QuestionAdmin(SummernoteModelAdmin):
    model = Question
    list_display = ('user', 'short_question', 'location', 'final_answer')
    list_filter = ('final_answer',)
    readonly_fields = ('full_user_description', 'question', 'answered',
                       'full_location', 'full_browser_location')
    fields = ('answered', 'full_user_description', 'full_location',
              'full_browser_location', 'question', 'answer', 'final_answer')

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

    def get_readonly_fields(self, request, obj):
        fields = super().get_readonly_fields(request, obj)
        if obj.final_answer:
            fields += ('answer',)
        return fields

    def short_question(self, instance):
        if len(instance.question) > 30:
            return instance.question[:30]+"..."
        else:
            return instance.question

admin.site.register(Question, QuestionAdmin)
