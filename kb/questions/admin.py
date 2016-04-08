from django.contrib import admin
from .models import Question

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_question', 'location', 'final_answer')
    list_filter = ('final_answer',)
    readonly_fields = ('answered',)

    def short_question(self, instance):
        if len(instance.question) > 30:
            return instance.question[:30]+"..."
        else:
            return instance.question

admin.site.register(Question, QuestionAdmin)
