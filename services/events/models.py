from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils import formats
from django.core.urlresolvers import reverse

from polymorphic import PolymorphicModel
from uuid import uuid4

from loader.models import App
from apps.news.models import TimestampedArticle

class Verb(models.Model):
    key = models.CharField(max_length=255)
    event_class = models.CharField(max_length=255)
    iri = models.URLField()
    description = models.TextField()
    
    def __str__(self):
        return str(self.key) +": "+ str(self.iri)
    
    def __repr__(self):
        return str(self)

class Event(PolymorphicModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    user = models.ForeignKey(User)
    verb = models.ForeignKey(Verb)

    #The object and result properties are set in the verb-specific subclasses
    #as the type of object or result can differ based on the verb used.
    
    app = models.ForeignKey(App)

    #This should be a foreign key to Group-Institute hierarchy, but that hasn't
    #been implemented yet.
    group = models.CharField(max_length=255)
    
    timestamp = models.DateTimeField(default=timezone.now)
    stored = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-timestamp"]

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        return u'Event'

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def describe(self):
        """Return a dictionary-like object with key properties."""
        displayname = (lambda user: u' '.join([user.first_name, user.last_name])
                if user.first_name else user.username)
        return {'date': formats.date_format(
                    timezone.localtime(self.timestamp),
                    "DATETIME_FORMAT"),
                'user': unicode(displayname(self.user)),
                'group': unicode(group),
                'app': unicode(app)
                }
    
    def create(app, group, user, verb, obj, result=None, timestamp=None):    
        #Should be wrapped with some try-excepts, but for now raising is fine
        _app = App.objects.get(pk=app)
        _verb = Verb.objects.get(key=verb)

        kwargs = {'user': User.objects.get(pk=user),
                  'verb': _verb,
                  'app': _app,
                  'group': group
                  }
        if timestamp:
            kwargs.update({'timestamp': timestamp})

        #eval(_verb.event_class).create(kwargs, obj, result)
        #Create specific subclass instance and a generic event instance with
        #with a pointer to the specific instance, thus the data is redundant
        subclass = ContentType.objects.get(app_label='events',
                model=_verb.event_class.lower())
        instance = subclass.model_class().create(kwargs, obj, result)
        #print(instance.pk)
        #print(str(instance))
        GenericEvent.objects.create(content_type=subclass,
                object_id=instance.pk, verb_instance=instance, **kwargs)
        
class GenericEvent(Event):
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    verb_instance = GenericForeignKey('content_type', 'object_id')

class ReadEvent(Event):
    article = models.ForeignKey(TimestampedArticle)
    
    def __unicode__(self):
        return u'%s' % (self.article.title,)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ReadEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'type': 'event-article-view',
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': unicode(self.article)
                }
            })
        return desc

    def create(kwargs, obj, res):
        article = TimestampedArticle.objects.get(pk=obj)
        return ReadEvent.objects.create(article=article, **kwargs)

class RatedEvent(Event):
    article = models.ForeignKey(TimestampedArticle)
    rating = models.IntegerField()

    def __unicode__(self):
        return u'%s' % (self.article.title,)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(RatedEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'type': 'event-article-rating',
            'rating': str(self.rating),
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': unicode(self.article)
                }
            })
        return desc

    def create(kwargs, obj, res):
        article = TimestampedArticle.objects.get(pk=obj)
        rating = int(res)
        return RatedEvent.objects.create(article=article, rating=rating, **kwargs)

class ScoredEvent(Event):
    article = models.ForeignKey(TimestampedArticle)
    rating = models.IntegerField()

    def __unicode__(self):
        return u'%s' % (self.article.title,)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ScoredEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'type': 'event-article-difficulty',
            'rating': str(self.rating),
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': unicode(self.article)
                }
            })
        return desc

    def create(kwargs, obj, res):
        article = TimestampedArticle.objects.get(pk=obj)
        rating = int(res)
        return ScoredEvent.objects.create(article=article, rating=rating, **kwargs)

class ClickedEvent(Event):
    article = models.ForeignKey(TimestampedArticle)
    word = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % (self.word,)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ClickedEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'type': 'event-word-cover',
            'word': unicode(self.word),
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': unicode(self.article)
                }
            })
        return desc

    def create(kwargs, obj, res):
        article = TimestampedArticle.objects.get(pk=obj)
        word = str(res)
        return RatedEvent.objects.create(article=article, word=word, **kwargs)

