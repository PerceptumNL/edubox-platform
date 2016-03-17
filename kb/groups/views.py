from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from collections import defaultdict

def group_list(request):
    from .models import Membership
    #If user is authenticated, retrieve all groups he is a member of
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    #For each group store all available apps and the complete parent-path
    group_contexts = {}
    #For each group count how many parent-paths traverse that group
    parent_counts = defaultdict(int)
    role = request.GET.get('role', None)
    if role is None:
        memberships = Membership.objects.filter(user=request.user.profile)
    else:
        memberships = Membership.objects.filter(user=request.user.profile,
                role__role=role)
    for membership in memberships:
        parent = membership.group
        parents = []
        while parent != None:
            parents.append(parent)
            parent_counts[parent] += 1
            parent = parent.parent

        group_contexts[membership] = parents

    #Remove all groups that shared in all parent-paths from the paths
    # i.e. the groups where the parent-path-count == the total number of groups
    group_count = len(group_contexts)
    for parent, count in parent_counts.items():
        if count == group_count:
            for parents in group_contexts.values():
                parents.remove(parent)

    group_exports = [];
    for membership, parents in group_contexts.items():
        parents = [parent.title for parent in parents[::-1]]
        group_exports.append({
            'id': membership.group.pk,
            'title': membership.group.title,
            'role': membership.role.role,
            'path': parents
        })

    group_exports = sorted(group_exports, key=lambda x: x['title'])

    return JsonResponse({'groups': group_exports});

def group_details(request, group_id):
    from .models import Group, Membership
    group = get_object_or_404(Group, pk=int(group_id))
    try:
        membership = Membership.objects.get(
            user=request.user.profile, group=group)
    except Membership.DoesNotExist:
        return HttpResponse(status=403);

    # TODO: Use permissions linked to the Role to determine access
    if membership.role.role == "Teacher":
        members = Membership.objects.filter(group=group).exclude(
            user=request.user.profile)
    else:
        members = Membership.objects.filter(
            group=group, role__role='Teacher').exclude(user=request.user.profile)

    members_export = []
    for member in members:
        members_export.append({
            'id': member.user.user.pk,
            'role': member.role.role,
            'name': member.user.full_name,
        })

    return JsonResponse({
        'id': group.pk,
        'title': group.title,
        'role': membership.role.role,
        'members': members_export
    })
