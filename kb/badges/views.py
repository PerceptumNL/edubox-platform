from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from .models import *
from kb import *

import json

@csrf_exempt
def get_badges():
    if 'app-token' not in request.GET:
        return HttpResponse(status=400)
    context = json.loads(request.context)
   
    try:
        user = UserProfile.objects.get(pk=int(context['user']))
        badge = Badge.objects.get(pk=int(badge_id))
    except (ObjectDoesNotExist, ValueError):
        return HttpResponse(status=400)

