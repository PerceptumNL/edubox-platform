from django.contrib import admin
from .models import ServerCookiejar, ServerCredentials

admin.site.register(ServerCookiejar)
admin.site.register(ServerCredentials)
