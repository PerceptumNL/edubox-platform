from django.db import models
from django.contrib.auth.models import User

from polymorphic import PolymorphicModel
from abc import ABCMeta
from uuid import uuid4


class Event(PolymorphicModel):
    __metaclass__ = ABCMeta
    verb_mapping = {'read': ReadEvent,
                    'rated': RatedEvent,
                    'scored': ScoredEvent,
                    'clicked': ClickedEvent}
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    actor = models.ForeignKey(User)
    
    #This should be a seperate class with verb = models.ForeignKey(Verb)
    #How to link subclasses to specific Verb instances?
    verb_iri = models.URLField()
    description = models.TextField

    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        return u'Event'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def xapi_id(self):
        return self.uuid

    def xapi_actor(self):
        return self.user

    def xapi_verb(self):
        return self.verb_iri, self.description

    @abstractproperty
    def xapi_object(self):
        pass

    @abstractproperty
    def xapi_result(self):
        pass

    def xapi_context(self):
        #App
        #School-Teacher
            #Retrieve from User?

    def xapi_timestamp(self):

    def xapi_stored(self):

    def xapi_authority(self):

    def xapi_version(self):

    def describe(self):
        """Return a dictionary-like object with key properties."""
        displayname = (lambda user: u' '.join([user.first_name, user.last_name])
                if user.first_name else user.username)
        return {'type': 'event',
                'date': formats.date_format(
                    timezone.localtime(self.date),
                    "DATETIME_FORMAT"),
                'user': unicode(displayname(self.user))
                }
    
    def create():
        #Static subclass constructor
        

class ReadEvent(Event):
    verb_iri  = "http://id.tincanapi.com/verb/viewed"
    description = ("Indicates that the actor has viewed the object. "
                   "For now this will mean 'has read article'.")
    
    article = models.ForeignKey('content.Article')

    def __unicode__(self):
        return u'%s' % (self.article.title,)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ArticleHistoryItem, self).describe()
        desc = {} if desc is None else desc
        desc.update({
            'type': 'event-article-view',
            'article': {
                'url': reverse('article', args=(self.article.id,)),
                'title': unicode(self.article)
                }
            })
        return desc


class RatedEvent(Event):
    verb_iri = "http://id.tincanapi.com/verb/rated"
    description = ("Action of giving a rating to an object. Should only be "
                   "used when the action is the rating itself, as opposed to "
                   "another action such as 'reading' where a rating can be "
                   "applied to the object as part of that action. In general "
                   "the rating should be included in the Result with a Score "
                   "object.")
    
    article = models.ForeignKey('content.Article')
    rating = models.IntegerField()

    def __unicode__(self):
        return u'%s' % (self.article.title,)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ArticleRatingItem, self).describe()
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

class ScoredEvent(Event):
    verb_iri = "http://adlnet.gov/expapi/verbs/scored"
    description = ("A measure related to learner performance, typically "
                   "between either 0 and 1 or 0 and 100, which corresponds to "
                   "learner performance on an activity. It is expected the "
                   "context property provides guidance to the allowed values "
                   "of the result field."
                   "For now this will mean 'rated article difficulty'.")
    
    article = models.ForeignKey('content.Article')
    rating = models.IntegerField()

    def __unicode__(self):
        return u'%s' % (self.article.title,)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(ArticleDifficultyItem, self).describe()
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

class ClickedEvent(Event):
    verb_iri = "http://adlnet.gov/expapi/verbs/interacted"
    description = ("A catch-all verb used to assert an actor's manipulation "
                   "of an object, physical or digital, in some context."
                   "For now this will mean 'clicked word'.")

    article = models.ForeignKey('content.Article')
    word = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % (self.word,)

    def describe(self):
        """Return a dictionary-like object with key properties."""
        desc = super(WordHistoryItem, self).describe()
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

