from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json

@csrf_exempt
def ask_question(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (ValueError, TypeError):
        return HttpResponse('Unsupported data type', status=400)

    if not ('question' in payload and 'location' in payload):
        return HttpResponse('Missing parameters', status=400)

    from .models import Question
    Question.objects.create(user=request.user.profile,
                            question=payload['question'],
                            location=payload['location'])
    return HttpResponse(status=204)
