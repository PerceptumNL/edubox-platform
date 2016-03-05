from django.http import JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from kb.helpers import create_token
from .models import LearningUnit
from kb.groups.models import Group

from .events import * # TODO: Find a better place for loading this.

def learning_units(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    group_id = request.GET.get('group', None)
    if group_id is None:
        return HttpResponse(status=400)

    group = get_object_or_404(Group, pk=int(group_id))

    # Fetch correct urlconf for accounts app login routing
    login_urlconf = settings.SUBDOMAIN_ROUTING.get('accounts',
        settings.ROOT_URLCONF)

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
            'login': "%s?token=%s" % (
                reverse('app_login', urlconf=login_urlconf), token),
            'token': token})

    return JsonResponse({'units': units})
