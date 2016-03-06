from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.conf import settings

from kb.groups.models import Group
from kb.helpers import create_token

def get_routed_app_url(request, app, url='/'):
    from urllib.parse import urlsplit, urlunsplit
    from binascii import b2a_hex
    from subdomains.utils import get_domain

    parts = urlsplit(url)
    domain = parts.netloc or urlsplit('http://'+app.root).netloc
    hashed_domain = "%s.%s" % (
        b2a_hex(bytes(domain, "utf-8")).decode("utf-8"), get_domain())

    return urlunsplit((
        settings.ROUTER_PROTOCOL or parts.scheme or request.scheme,
        hashed_domain,
        parts.path,
        parts.query,
        parts.fragment))

def launch_app(request, group_id, app_id):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)
    from kb.apps.models import App
    group = get_object_or_404(Group, pk=group_id)
    app = get_object_or_404(App, pk=app_id)

    # TODO: Ensure user has access to that app in that group

    token = create_token(user=request.user.pk, group=group.pk, app=app.pk)
    location = get_routed_app_url(request, app)

    return HttpResponseRedirect(
            "%s?token=%s" % (location, token.decode('utf-8')))

def launch_unit(request, group_id, unit_id):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)
    from kb.collections.models import LearningUnit
    group = get_object_or_404(Group, pk=group_id)
    unit = get_object_or_404(LearningUnit, pk=unit_id)
    # TODO: Ensure user has access to that unit in that group

    activity = unit.get_next_activity_for_user(request.user)

    if activity is not None:
        token = create_token(user=request.user.pk, group=group.pk,
            app=activity.app.pk)
        location = get_routed_app_url(request, activity.app,
                activity.url)

        return HttpResponseRedirect(
                "%s?token=%s" % (location, token.decode('utf-8')))
    else:
        return HttpResponseRedirect('/')
