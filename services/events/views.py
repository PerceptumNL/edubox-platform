from django.http import HttpResponse
from django.views.generic import View

from .models import Event

import json


class API(View)

    def get(self, request):
        #TODO: Implement filters
        return HttpResponse()

    def get_event(event):
        try:
            return json.dumps(Event.objects.get(pk=event).describe())
        except Event.DoesNotExist:
            return HttpResponse(status=400)

    def post(self, request):
        events = json.loads(request.POST)
        if type(events)==list:
            for event in events:
                resp = post_event(event)
                if resp.status_code == 400:
                    return resp
        else:
            return post_event(events)

    def post_event(event):
        try:
            #Event.create(**event)
            print(event)
            return HttpResponse()
        except TypeError:
            return HttpResponse(status=400)

