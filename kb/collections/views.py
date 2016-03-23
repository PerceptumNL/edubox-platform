from django.http import JsonResponse, HttpResponse
from subdomains.utils import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from kb.helpers import create_token
from .models import LearningUnit, Challenge
from kb.groups.models import Group
from launch.helpers import route_links_in_text

from .events import * # TODO: Find a better place for loading this.

def list_all(request):
    """Catch all view that combines results from units and challenges."""
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    group_id = request.GET.get('group', None)
    if group_id is None:
        return HttpResponse(status=400)

    group = get_object_or_404(Group, pk=int(group_id))

    login_base = reverse('app_login', subdomain='accounts',
            scheme=request.scheme)

    units = []
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

    challenges = []
    # TODO: Actually make this list group dependant.
    for challenge in Challenge.objects.all():
        challenges.append({
            'id': challenge.pk,
            'label': challenge.label,
            'url': route_links_in_text(request, challenge.url, group),
            'details': "%s/?group=%s" % (
                reverse("collections_challenge_detail", args=(challenge.pk,),
                        subdomain="api",scheme=request.scheme),
                group_id),
            'body': route_links_in_text(request, challenge.body, group),
            })

    return JsonResponse({'items': {'units': units, 'challenges': challenges}})


def list_units(request):
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
    for unit in LearningUnit.objects.order_by('order').all():
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

def list_challenges(request):
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
            'url': route_links_in_text(request, challenge.url, group),
            'details': "%s/?group=%s" % (
                reverse("collections_challenge_detail", args=(challenge.pk,),
                        subdomain="api",scheme=request.scheme),
                group_id),
            'body': route_links_in_text(request, challenge.body, group),
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

    return JsonResponse({
        'id': challenge.pk,
        'label': challenge.label,
        'url': route_links_in_text(request, challenge.url, group),
        'body': route_links_in_text(request, challenge.body, group)})
