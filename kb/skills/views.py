from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

def skill_export_by_user(user):
    from kb.badges.models import UserBadge, Badge
    skills = UserBadge.objects.filter(user=user,
            badge__badge_type=Badge.T_SKILL_BADGE)
    skill_export = []
    for skill in skills:
        skill_export.append({
            "skill": {
                "id": skill.badge.pk,
                "title": skill.badge.title,
                "description": skill.badge.description
            },
            "level": {
                "id": skill.level.pk,
                "index": skill.level.index
            },
            "xp": skill.xp
        });
    return skill_export

# Create your views here.
def get_skills(request):
    from kb.groups.models import Group, Membership
    group = request.GET.get('group')
    if group is not None:
        group = get_object_or_404(Group, pk=group)
        if not request.user.profile.is_teacher(group):
            return HttpResponse(status=403)

        group_skill_export = []
        for member in Membership.objects.filter(group=group):
            group_skill_export.append({
                'id': member.user.user.pk,
                'role': member.role.role,
                'name': member.user.full_name,
                'skills': skill_export_by_user(member.user)
            })
        return JsonResponse({'skills': group_skill_export})
    else:
        skill_export = skill_export_by_user(request.user.profile)
        return JsonResponse({'skills': skill_export})
