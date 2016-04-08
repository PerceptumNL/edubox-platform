from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'datetime')
    readonly_fields = ('read',)

admin.site.register(Message, MessageAdmin)
