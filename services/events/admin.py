from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from .models import *

class ClickedEventAdmin(PolymorphicChildModelAdmin):
    base_model = ClickedEvent
    list_display = ('user', 'word', 'article', 'timestamp')


class ReadEventAdmin(PolymorphicChildModelAdmin):
    base_model = ReadEvent
    list_display = ('user', 'article', 'timestamp')


class RatedEventAdmin(PolymorphicChildModelAdmin):
    base_model = RatedEvent
    list_display = ('user', 'rating', 'article', 'timestamp')


class ScoredEventAdmin(PolymorphicChildModelAdmin):
    base_model = ScoredEvent
    list_display = ('user', 'rating', 'article', 'timestamp')


class EventAdmin(PolymorphicParentModelAdmin):
    base_model = Event
    list_display = ('user', 'get_type', 'get_article', 'get_value', 'timestamp')
    
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (ReadEvent, ReadEventAdmin),
        (ClickedEvent, ClickedEventAdmin),
        (RatedEvent, RatedEventAdmin),
        (ScoredEvent, ScoredEventAdmin)
    )

    def get_type(self, obj):
        crt_class = type(obj.get_real_instance()).__name__
        if crt_class=='ReadEvent':
            return "Read"
        elif crt_class=='ClickedEvent':
            return "Clicked word"
        elif crt_class=='RatedEvent':
            return "Rated Article"
        elif crt_class=='ScoredEvent':
            return "Rated Difficulty"
        else:
            return crt_class
    def get_article(self, obj):
        return str(obj.get_real_instance().article)
    get_article.short_description = 'Article'
    def get_value(self, obj):
        crt_class = type(obj.get_real_instance()).__name__
        if crt_class=='ClickedEvent':
            return obj.get_real_instance().word
        elif crt_class=='RatedEvent':
            return obj.get_real_instance().rating
        elif crt_class=='ScoredEvent':
            return obj.get_real_instance().rating
        else:
            return ""
    get_value.short_description = 'Value'


admin.site.register(Verb)
admin.site.register(Context)
admin.site.register(Event, EventAdmin)
