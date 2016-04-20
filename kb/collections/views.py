from django.http import JsonResponse, HttpResponse
from subdomains.utils import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from kb.helpers import create_token
from kb.groups.models import Group
from kb.events.models import GenericEvent
from launch.helpers import route_links_in_text, get_app_by_url, get_routed_app_url

from .models import LearningUnit, Challenge, ActivityCompletion
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
        app = get_app_by_url(challenge.url)
        if app is not None:
            token = create_token(
                request.user.pk,
                group.pk,
                app.pk).decode('utf-8')
            login_url = "%s?token=%s" % (login_base, token)
        else:
            token = None
            login_url = None

        challenges.append({
            'id': challenge.pk,
            'label': challenge.label,
            'url': route_links_in_text(request, challenge.url, group),
            'login': login_url,
            'token': token,
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
        if activity is None:
            activity = unit.activities.first()
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

def unit_detail(request, unit_id):
    """Return unit info and activities."""
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    group_id = request.GET.get('group', None)
    if group_id is None:
        return HttpResponse(status=400)

    group = get_object_or_404(Group, pk=int(group_id))
    unit = get_object_or_404(LearningUnit, pk=int(unit_id))

    url_from_activity = (lambda a, r, t: "%s?token=%s" % (
        get_routed_app_url(r, a.app, a.url), t))

    next_activity = unit.get_next_activity_for_user(request.user)
    if next_activity is not None:
        token = create_token(
            request.user.pk,
            group.pk,
            next_activity.app.pk).decode('utf-8')
        login_base = reverse('app_login', subdomain='accounts',
                scheme=request.scheme)
        login_url = "%s?token=%s" % (login_base, token)
    else:
        login_url = None

    fn_cutoff_protocol = lambda u: u.replace('https:','').replace('http:','')

    activities = unit.activities.all()
    activity_completions = ActivityCompletion.objects.filter(
        user=request.user.profile)
    progress = {}
    for completion in activity_completions:
        progress[fn_cutoff_protocol(completion.activity.url)] = (
            'perfect' if completion.score == 100.0 else 'completed')
    activity_urls = []
    for activity in activities:
        if fn_cutoff_protocol(activity.url) not in progress:
            activity_urls.append(fn_cutoff_protocol(activity.url))

    activity_events = GenericEvent.objects.filter(obj__in=activity_urls,
            user=request.user)
    for activity_event in activity_events:
        progress[activity_event.obj] = 'pending'

    return JsonResponse({
            'id': unit.pk,
            'completed': not bool(next_activity),
            'label': unit.label,
            'description': unit.description,
            'login': login_url,
            'launch': url_from_activity(next_activity, request, token) if \
                    next_activity else None,
            'token': token,
            'activities': [{
                'id': activity.id,
                'state': progress.get(fn_cutoff_protocol(activity.url),
                    'unstarted'),
                'token': create_token(
                    request.user.pk,
                    group.pk,
                    activity.app.pk).decode('utf-8'),
                'launch': url_from_activity(
                    activity,
                    request,
                    create_token(
                        request.user.pk,
                        group.pk,
                        activity.app.pk).decode('utf-8')),
                'label': activity.label} for activity in activities]
    })

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
