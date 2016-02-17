from django.contrib import admin
from .models import LearningUnit, Activity, ActivityCompletion

admin.site.register(LearningUnit)
admin.site.register(Activity)
admin.site.register(ActivityCompletion)
