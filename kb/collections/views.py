import re

from django.http import JsonResponse, HttpResponse
from subdomains.utils import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from kb.helpers import create_token
from .models import LearningUnit, Challenge
from kb.groups.models import Group

from .events import * # TODO: Find a better place for loading this.

def learning_units(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    group_id = request.GET.get('group', None)
    if group_id is None:
        return HttpResponse(status=400)

    group = get_object_or_404(Group, pk=int(group_id))

    units = []
    login_base = reverse('app_login', subdomain='accounts',
            scheme=request.scheme)
    # TODO: Actually make this list group dependant.
    for unit in LearningUnit.objects.all():
        activity = unit.get_next_activity_for_user(request.user)
        token = create_token(
            request.user.pk,
            group.pk,
            activity.app.pk).decode('utf-8')
        units.append({
            'id': unit.pk,
            'label': unit.label,
            'login': "%s?token=%s" % (login_base, token),
            'token': token})

    return JsonResponse({'units': units})

def challenges(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    group_id = request.GET.get('group', None)
    if group_id is None:
        return HttpResponse(status=400)

    group = get_object_or_404(Group, pk=int(group_id))

    challenges = []

    # TODO: Actually make this list group dependant.
    for challenge in Challenge.objects.all():
        challenges.append({
            'id': challenge.pk,
            'label': challenge.label,
            'details': "%s/?group=%s" % (
                reverse("challenge_detail", args=(challenge.pk,),
                        subdomain="api",scheme=request.scheme),
                group_id),
            })

    return JsonResponse({'challenges': challenges})

def challenge_detail(request, challenge_id):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    group_id = request.GET.get('group', None)
    if group_id is None:
        return HttpResponse(status=400)

    group = get_object_or_404(Group, pk=int(group_id))
    challenge = get_object_or_404(Challenge, pk=int(challenge_id))

    rgx = r'(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w\.-]*)*\/?'

    group_apps = group.apps.all()

    challenge_body = challenge.body
    links = re.findall(rgx, challenge_body)
    from launch.helpers import get_routed_url
    for link in links:
        for app in group_apps:
            if re.match(app.identical_urls, link):
                break
        else:
            break

        token = create_token(
            request.user.pk,
            group.pk,
            app.pk).decode('utf-8')
        challenge_body = challenge_body.replace(link, "%s?token=%s" % (
            get_routed_url(request, link), token))

    return JsonResponse({
        'id': challenge.pk,
        'label': challenge.label,
        'body': challenge_body})
