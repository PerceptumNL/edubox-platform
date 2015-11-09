from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

from .models import Event, Verb

import json

class API(View):

    def get(self, request):
        """Test Docstring"""
        if 'verb' not in request.GET or 'filter' not in request.GET:
            return HttpResponse(status=400)

        verb = Verb.objects.get(key=request.GET.get('verb'))
        subclass = ContentType.objects.get(app_label='events',
                model=verb.event_class.lower()).model_class()
        
        filt = request.GET.get('filter')
        if filt == 'all':
            return self.get_all(subclass)
        else:
            return HttpResponse(status=400)

    def get_all(self, event_class):
        return HttpResponse(json.dumps([event.describe() for event in 
                event_class.objects.all()]))

    def post(self, request):
        events = json.loads(str(request.body, 'utf-8'))
        if type(events)==list:
            for event in events:
                resp = self.post_event(event)
                if resp.status_code == 400:
                    return resp
            return HttpResponse()
        else:
            return self.post_event(events)

    def post_event(self, event):
        try:
            Event.create(**event)
            return HttpResponse()
        except TypeError:
            return HttpResponse(status=400)
    
    #This means the API is completely open and thus all permissions should
    #be thoroughly checked in the view functions
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(API, self).dispatch(*args, **kwargs)

