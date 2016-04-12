from django.contrib import admin
from .models import Release, ReleaseItem

class ReleaseItemInline(admin.TabularInline):
    model = ReleaseItem

class ReleaseAdmin(admin.ModelAdmin):
    inlines = [ ReleaseItemInline ]

admin.site.register(Release, ReleaseAdmin)
