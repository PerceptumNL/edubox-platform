from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from kb.groups.models import Group
from kb.helpers import create_token
from router import AppRouter

def launch_app(request, group_id, app_id):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)
    from kb.apps.models import App
    group = get_object_or_404(Group, pk=group_id)
    app = get_object_or_404(App, pk=app_id)

    # TODO: Ensure user has access to that app in that group

    token = create_token(user=request.user.pk, group=group.pk, app=app.pk)
    location = AppRouter.get_routed_app_url(request, app)

    return HttpResponseRedirect(
            "%s/?token=%s" % (location, token.decode('utf-8')))

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
        location = AppRouter.get_routed_app_url(request, activity.app,
                activity.url)

        return HttpResponseRedirect(
                "%s/?token=%s" % (location, token.decode('utf-8')))
    else:
        return HttpResponseRedirect('/')
