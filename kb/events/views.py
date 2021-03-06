from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

from .models import Verb, Event, GenericEvent

import json
import datetime
import sys
import debugutil

class API(View):

    # Filters implemented in _filter_verb
    filters = ['user', 'group', 'app', 'before', 'after']

    def get(self, request):
        if 'verb' in request.GET:
            try:
                verb = Verb.objects.get(iri=request.GET.get('verb'))
            except Verb.DoesNotExist:
                return HttpResponse(status=400)

            verb_class = ContentType.objects.get(app_label='events',
                    model=verb.event_class.lower()).model_class()
        else:
            verb_class = GenericEvent

        verb_filters = {}
        for filt in self.filters:
            if filt in request.GET:
                verb_filters[filt] = request.GET.get(filt)

        events = self._filter_verb(verb_class, **verb_filters)
        if events == None:
            return HttpResponse(status=400)

        if 'detail' in request.GET and request.GET.get('detail') == 'simple':
            dump = [super(verb_class, event).describe() for event in events]
        else:
            dump = [event.describe() for event in events]

        return HttpResponse(json.dumps(dump))

    def _filter_verb(self, verb_class, **kwargs):
        events = verb_class.objects.all()

        if 'user' in kwargs:
            events = events.filter(user__username=kwargs['user'])
        if 'group' in kwargs:
            events = events.filter(group__title=kwargs['group'])
        if 'app' in kwargs:
            events = events.filter(app__title=kwargs['app'])
        if 'before' in kwargs:
            date = _date_instance(kwargs['before'])
            if date == None:
                return None
            events = events.filter(timestamp__lt=date)
        if 'after' in kwargs:
            date = _date_instance(kwargs['after'])
            if date == None:
                return None
            events = events.filter(timestamp__gt=date)
        return events

    def post(self, request):
        events = json.loads(str(request.body, 'utf-8'))
        context = json.loads(request.context)

        if type(events)==list:
            for event in events:
                resp = self._post_event(event, context)
                if resp.status_code == 400:
                    return resp
            return HttpResponse()
        else:
            return self._post_event(events, context)

    def _post_event(self, event, context):
        event.update(context)
        try:
            Event.create(**event)
        except (TypeError, AttributeError) as err:
            self._debug(420, info=str(err))
            return HttpResponse(status=400)

        return HttpResponse()

    #This means the API is completely open and thus all permissions should
    #be thoroughly checked in the view functions
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(API, self).dispatch(*args, **kwargs)

    def _debug(self, *args, **kwargs):
        """
        Wrapper function for debugutil.debug, setting the logger based on the
        value of the class name and the function that called
        this debug function.
        """
        logger_name = "%s.%s" % (
            __name__, sys._getframe().f_back.f_code.co_name)
        debugutil.debug(*args, logger=logger_name, **kwargs)

def _date_instance(date):
    """Convert string tot datetime instance according to ISO 8601"""
    try:
        kwargs = dict(zip(['year', 'month', 'day'], [int(x) for x in date.split('-')]))
        return datetime.date(**kwargs)
    except (TypeError, ValueError):
        return None

