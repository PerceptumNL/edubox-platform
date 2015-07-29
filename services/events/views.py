from django.shortcuts import render

from .models import Event

import json


def post_events(data):
    events = json.loads(data)
    if type(events)==list:
        for event in events:
            resp = post_event(event)
            if resp.status_code == 400:
                return resp
    else:
        return post_event(events)

def post_event(event):
    try:
        Event.create(**event)
        return HttpResponse()
    except TypeError:
        return HttpResponse(status=400)

def get_events():
    #TODO: Implement filters
    pass

def get_event(event):
    return json.dumps(Event.objects.get(pk=event).describe())
