from django.http import JsonResponse, HttpResponse
from subdomains.utils import reverse
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
