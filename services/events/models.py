from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils import formats
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from uuid import uuid4

from router.models import App
from services.usermanagement.models import Group
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

class Event(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    user = models.ForeignKey(User)
    verb = models.ForeignKey(Verb)

    #The object and result properties are set in the verb-specific subclasses
    #as the type of object or result can differ based on the verb used.
    
    app = models.ForeignKey(App)

    #This should be a foreign key to Group-Institute hierarchy, but that hasn't
    #been implemented yet.
    group = models.ForeignKey(Group)
    
    timestamp = models.DateTimeField(default=timezone.now)
    stored = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-timestamp"]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ('at '+ formats.date_format(timezone.localtime(self.timestamp),
                'DATETIME_FORMAT') +' in '+ self.app.title +' : '+
                self.user.username +' '+ self.verb.key +' ')

    def describe(self):
        """Return a dictionary-like object with key properties."""
        return {'date': formats.date_format(
                    timezone.localtime(self.timestamp),
                    "DATETIME_FORMAT"),
                'user': str(self.user.username),
                'group': str(self.group),
                'app': str(self.app)
                }
    
    def create(app, group, user, verb, obj, result=None, timestamp=None):    
        try:
            _verb = Verb.objects.get(key=verb)
            kwargs = {'user': User.objects.get(pk=user),
                      'verb': _verb,
                      'group': Group.objects.get(pk=group),
                      'app': App.objects.get(pk=app)
                      }
        except (ObjectDoesNotExist, ValueError):
            raise AttributeError()

        if timestamp:
            kwargs.update({'timestamp': timestamp})

        #Create a verb-specific subclass instance
        subclass = ContentType.objects.get(app_label='events',
                model=_verb.event_class.lower())
        instance = subclass.model_class().create(kwargs, obj, result)
        
        #If creation of the instance with these kwargs failed
        if instance == None:
            raise AttributeError()
        
        #Generic event instance with a pointer to the specific instance
        GenericEvent.objects.create(content_type=subclass,
                object_id=instance.pk, verb_instance=instance, **kwargs)
        
class GenericEvent(Event):
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    verb_instance = GenericForeignKey('content_type', 'object_id')

class ReadEvent(Event):
    article = models.ForeignKey(TimestampedArticle)
    
    def __str__(self):
        return super(ReadEvent, self).__str__() + self.article.title

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ReadEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'verb': 'read',
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': str(self.article)
                }
            })
        return desc

    def create(kwargs, obj, res):
        try:
            article = TimestampedArticle.objects.get(pk=obj)
        except (ObjectDoesNotExist, ValueError):
            return None
        return ReadEvent.objects.create(article=article, **kwargs)

class RatedEvent(Event):
    article = models.ForeignKey(TimestampedArticle)
    rating = models.IntegerField()

    def __str__(self):
        return super(RatedEvent, self).__str__() + self.article.title

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(RatedEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'verb': 'rated',
            'rating': str(self.rating),
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': str(self.article)
                }
            })
        return desc

    def create(kwargs, obj, res):
        try:
            article = TimestampedArticle.objects.get(pk=obj)
            rating = int(res)
        except (ObjectDoesNotExist, ValueError):
            return None
        return RatedEvent.objects.create(article=article, rating=rating, **kwargs)

class ScoredEvent(Event):
    article = models.ForeignKey(TimestampedArticle)
    rating = models.IntegerField()

    def __str__(self):
        return super(ScoredEvent, self).__str__() + self.article.title

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ScoredEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'verb': 'scored',
            'rating': str(self.rating),
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': str(self.article)
                }
            })
        return desc

    def create(kwargs, obj, res):
        try:
            article = TimestampedArticle.objects.get(pk=obj)
            rating = int(res)
        except (ObjectDoesNotExist, ValueError):
            return None
        return ScoredEvent.objects.create(article=article, rating=rating, **kwargs)

class ClickedEvent(Event):
    article = models.ForeignKey(TimestampedArticle)
    word = models.CharField(max_length=255)

    def __str__(self):
        return super(ClickedEvent, self).__str__() + self.word

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ClickedEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'verb': 'clicked',
            'word': str(self.word),
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': str(self.article)
                }
            })
        return desc

    def create(kwargs, obj, res):
        try:
            article = TimestampedArticle.objects.get(pk=obj)
        except (ObjectDoesNotExist, ValueError):
            return None
        return RatedEvent.objects.create(article=article, word=str(res), **kwargs)

