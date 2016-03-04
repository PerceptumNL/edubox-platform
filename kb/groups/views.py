from django.http import JsonResponse, HttpResponse

from collections import defaultdict

def group_list(request):
    #If user is authenticated, retrieve all groups he is a member of
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    #For each group store all available apps and the complete parent-path
    group_contexts = {}
    #For each group count how many parent-paths traverse that group
    parent_counts = defaultdict(int)
    for group in request.user.profile.groups.all():
        parent = group
        parents = []
        while parent != None:
            parents.append(parent)
            parent_counts[parent] += 1
            parent = parent.parent

        group_contexts[group] = parents

    #Remove all groups that shared in all parent-paths from the paths
    # i.e. the groups where the parent-path-count == the total number of groups
    group_count = len(group_contexts)
    for parent, count in parent_counts.items():
        if count == group_count:
            for parents in group_contexts.values():
                parents.remove(parent)

    group_exports = [];
    for group, parents in group_contexts.items():
        group_exports.append(
            {'id': group.pk, 'title': group.title, 'path': parents })

    return JsonResponse({'groups': group_exports});
