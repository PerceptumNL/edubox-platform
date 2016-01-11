from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from kb.apps.models import App
from kb.groups.models import Group
from kb.helpers import create_token
from router import AppRouter

def launch_app(request, group_id, app_id):
    group = get_object_or_404(Group, pk=group_id)
    app = get_object_or_404(App, pk=app_id)

    # TODO: Ensure user has access to that app in that group

    token = create_token(user=request.user.pk, group=group.pk, app=app.pk)
    location = AppRouter.get_routed_app_root(request, app)

    return HttpResponseRedirect(
            "%s/?token=%s" % (location, token.decode('utf-8')))
