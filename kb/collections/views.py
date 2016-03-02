from django.http import JsonResponse, HttpResponse
from django.core.urlresolvers import reverse

from collections import defaultdict

from kb.helpers import create_token
from .models import LearningUnit

def learning_units(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    groups = request.user.profile.groups.all()

    #For each group store all available units and the complete parent-path
    group_contexts = {}
    #For each group count how many parent-paths traverse that group
    parent_counts = defaultdict(int)
    # TODO: Actually make this list group dependant.
    group_units = LearningUnit.objects.all()
    for group in groups:
        parent = group
        parents = []
        while parent != None:
            parents.append(parent)
            parent_counts[parent] += 1
            parent = parent.parent

        group_contexts[group] = (group_units, parents)

    #Remove all groups that shared in all parent-paths from the paths
    # i.e. the groups where the parent-path-count == the total number of groups
    group_count = len(group_contexts)
    for parent, count in parent_counts.items():
        if count == group_count:
            for context in group_contexts.values():
                context[1].remove(parent)

    #For each possible unit-group context store the name, description, icon,
    # trimmed-path and the computed context token, stored seperately for each group
    unit_groups = []
    for group, (units, parents) in group_contexts.items():
        unit_views = []
        parents = [parent.title for parent in parents[::-1]]
        for unit in units:
            activity = unit.get_next_activity_for_user(request.user)
            unit_views.append({
                'id': unit.pk,
                'label': unit.label,
                'login': "%s?token=%s" % (
                    reverse('app_login'),
                    create_token(request.user.pk, group.pk, activity.app.pk)),
                'path': parents })
        unit_groups.append({'id': group.pk, 'title': group.title,
            'units': unit_views})

    return JsonResponse({'units': unit_groups})
