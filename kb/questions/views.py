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

    if not ('question' in payload and 'location' in payload
            and 'browser' in payload):
        return HttpResponse('Missing parameters', status=400)

    payload['browser'] = payload['browser'] or ""

    from .models import Question
    question_obj = Question.objects.create(user=request.user.profile,
                                           question=payload['question'],
                                           browser_location=payload['browser'],
                                           location=payload['location'])

    # Notify moderators that a question was asked.
    from django.core.mail import send_mail
    from django.conf import settings
    from subdomains.utils import reverse
    msg = """
Dear moderator,

The following question was asked on the Codecult platform by %(user)s of
%(institute)s:

\"\"\"

%(question)s

\"\"\"

To answer this question go to the following link and provide the answer.
%(backend_url)s

When the answer can be considered to be final, check the box that says 'Final Answer'.
The answer will then be visible in the user's inbox.

The CodeCult Platform
"""
    send_mail('Question asked on CodeCult Platform',
            msg % {
                'user': request.user.profile.full_name,
                'institute': str(request.user.profile.institute),
                'question': payload['question'],
                'backend_url': reverse(
                    "admin:questions_question_change",
                    args=(question_obj.pk,),
                    subdomain='backend',
                    scheme=request.scheme)},
            settings.DEFAULT_FROM_EMAIL,
            settings.MODERATOR_EMAILS,
            fail_silently=True)
    return HttpResponse(status=204)
