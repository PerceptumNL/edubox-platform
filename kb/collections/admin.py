from django.contrib import admin
from .models import LearningUnit, Activity, ActivityCompletion

class ActivityCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_full_name',
                    'activity', 'datetime', 'institute')
    list_filter = ('user__institute',)
    search_fields = (
        'user__user__username',
        'user__user__email',
        'user__alias',
        'user__user__last_name',
        'user__user__first_name',
        'user__institute__title')

    def user_full_name(self, instance):
        return instance.user.full_name

    def institute(self, instance):
        return instance.user.institute.title

admin.site.register(LearningUnit)
admin.site.register(Activity)
admin.site.register(ActivityCompletion, ActivityCompletionAdmin)
