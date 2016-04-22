from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils import formats
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from uuid import uuid4

from kb.models import App
from kb.groups.models import Group

class Verb(models.Model):
    event_class = models.CharField(max_length=255)
    iri = models.URLField()
    description = models.TextField()

    def __str__(self):
        return str(self.iri)

    def __repr__(self):
        return str(self)


class Event(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    user = models.ForeignKey(User)
    verb = models.URLField(max_length=255)
    obj = models.URLField(max_length=255)

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
                self.user.username +' '+ self.verb +' '+ self.obj +' ')

    def describe(self):
        """Return a dictionary-like object with key properties."""
        return {'user': str(self.user.username),
                'verb': str(self.verb),
                'obj': str(self.obj),
                'group': str(self.group),
                'app': str(self.app),
                'date': formats.date_format(
                    timezone.localtime(self.timestamp),
                    "DATETIME_FORMAT"),
                }

    def create(app, group, user, verb, obj, result=None, timestamp=None):
        try:
            _verb = Verb.objects.get(iri=verb)
            kwargs = {'user': User.objects.get(pk=user),
                      'verb': verb,
                      'obj': obj.replace('https:','').replace('http:',''),
                      'group': Group.objects.get(pk=group),
                      'app': App.objects.get(pk=app)
                      }
        except (ObjectDoesNotExist, ValueError) as err:
            raise AttributeError(str(err))

        if timestamp:
            kwargs.update({'timestamp': timestamp})

        #Create a verb-specific subclass instance
        subclass = ContentType.objects.get(app_label='events',
                model=_verb.event_class.lower())
        instance = subclass.model_class().create(kwargs, result)

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


class SubmittedEvent(Event):
    submission = models.TextField();

    def create(kwargs, submission):
        try:
            return SubmittedEvent.objects.create(submission=submission, **kwargs)
        except ValueError:
            return None

class ReadEvent(Event):

    def create(kwargs, res=None):
        try:
            return ReadEvent.objects.create(**kwargs)
        except ValueError:
            return None

class RatedEvent(Event):
    rating = models.IntegerField()
    min_rating = models.IntegerField(default=0)
    max_rating = models.IntegerField(default=5)

    def __str__(self):
        return super(RatedEvent, self).__str__() + str(self.rating)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(RatedEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'rating': str(self.rating)})
        return desc

    def create(kwargs, res):
        try:
            return RatedEvent.objects.create(
                rating=int(res['rating']),
                min_rating=int(res['min_rating']),
                max_rating=int(res['max_rating']),
                **kwargs)
        except ValueError:
            return None


class ScoredEvent(Event):
    rating = models.IntegerField()

    def __str__(self):
        return super(ScoredEvent, self).__str__() + self.rating

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ScoredEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'rating': str(self.rating)})
        return desc

    def create(kwargs, res):
        try:
            return ScoredEvent.objects.create(rating=int(res), **kwargs)
        except ValueError:
            return None


class ClickedEvent(Event):
    page = models.URLField(max_length=255)

    def __str__(self):
        return super(ClickedEvent, self).__str__() + str(self.page)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ClickedEvent, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'page': str(self.word)})
        return desc

    def create(kwargs, res):
        try:
            return RatedEvent.objects.create(page=str(res), **kwargs)
        except ValueError:
            return None

