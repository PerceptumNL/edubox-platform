from django.contrib import admin

from .models import *
from django_summernote.admin import SummernoteModelAdmin
from polymorphic.admin import PolymorphicParentModelAdmin, \
        PolymorphicChildModelAdmin

class RSSFeedAdmin(PolymorphicChildModelAdmin):
    base_model = RSSFeed


class SevenDaysFeedAdmin(PolymorphicChildModelAdmin):
    base_model = SevenDaysFeed


class RegularContentFeedAdmin(PolymorphicChildModelAdmin):
    base_model = ContentFeed


class ContentFeedAdmin(PolymorphicParentModelAdmin):
    base_model = ContentFeed
    child_models = (
        (RSSFeed, RSSFeedAdmin),
        (SevenDaysFeed, SevenDaysFeedAdmin),
        (KidsWeekFeed, SevenDaysFeedAdmin),
        (ContentFeed, RegularContentFeedAdmin)
    )


class FeedArticleAdmin(PolymorphicChildModelAdmin):
    base_model = FeedArticle


class RegularArticleAdmin(PolymorphicChildModelAdmin):
    base_model = FeedArticle


class ArticleAdmin(PolymorphicParentModelAdmin):
    base_model = TimestampedArticle
    polymorphic_list = True
    search_fields = ['title',]
    list_display = ('title', 'main_category', 'publication_date',)
    list_filter = ('categories',)

    child_models = (
        (FeedArticle, FeedArticleAdmin),
        (TimestampedArticle, RegularArticleAdmin)
    )

    def main_category(self, obj):
        return obj.categories.first()


class ContentSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'logo')


admin.site.register(ContentFeed, ContentFeedAdmin)
admin.site.register(Category)
admin.site.register(TimestampedArticle, ArticleAdmin)
admin.site.register(ContentSource, ContentSourceAdmin)
