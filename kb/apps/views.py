from django.http import JsonResponse
from django.contrib.auth.models import User

from kb.helpers import create_token

from collections import defaultdict

def app_list(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)
    groups = request.user.userprofile.groups.all()

    group_contexts = {}
    parent_counts = defaultdict(int)
    for group in groups:
        parent = group
        parents = []
        while parent != None:
            parents.append(parent)
            parent_counts[parent] += 1
            parent = parent.parent

        group_contexts[group] = (group.apps.all(), parents)

    group_count = len(group_contexts)
    for parent, count in parent_counts.items():
        if count == group_count:
            for context in group_contexts.values():
                context[1].remove(parent)

    app_view = {}
    for group, (apps, parents) in group_contexts.items():
        context = []
        parents = [parent.title for parent in parents[::-1]]
        for app in apps:
            context.append({'name': app.title, 'icon': app.icon, 'path': parents,
                'token': create_token(user=request.user.pk, group=group.pk,
                app=app.pk).decode('utf-8')})

        app_view[group.title] = context

    return JsonResponse({'groups':app_view})

