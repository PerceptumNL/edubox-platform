from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets

from .models import Event, ReadEvent
from .serializers import ReadEventSerializer

import json

class API(View):

    def get(self, request):
        #TODO: Implement filters
        return HttpResponse()

    def get_event(self, event):
        try:
            return json.dumps(Event.objects.get(pk=event).describe())
        except Event.DoesNotExist:
            return HttpResponse(status=400)
    
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

class ReadEventViewSet(viewsets.ModelViewSet):
    queryset = ReadEvent.objects.all()
    serializer_class = ReadEventSerializer

