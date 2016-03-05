from django.contrib import admin

from .models import *

admin.site.register(Verb)
admin.site.register(GenericEvent)
admin.site.register(ReadEvent)
admin.site.register(RatedEvent)
admin.site.register(ScoredEvent)
admin.site.register(ClickedEvent)
admin.site.register(SubmittedEvent)
