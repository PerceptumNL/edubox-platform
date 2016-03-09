from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

def skill_export_by_user(user):
    from kb.badges.models import UserBadge, Badge
    user_skills = UserBadge.objects.filter(user=user,
            badge__badge_type=Badge.T_SKILL_BADGE)
    skill_export = {}
    for user_skill in user_skills:
        skill_export[user_skill.badge.pk] = {
            "id": user_skill.badge.pk,
            "title": user_skill.badge.title,
            "description": user_skill.badge.description,
            "level": {
                "id": user_skill.level.pk,
                "index": user_skill.level.index
            },
            "xp": user_skill.xp
        };
    skills = Badge.objects.filter(badge_type=Badge.T_SKILL_BADGE)
    for skill in skills:
        if skill.pk not in skill_export:
            skill_export[skill.pk] = {
                "id": skill.pk,
                "title": skill.title,
                "description": skill.description,
                "level": {
                    "id": None,
                    "index": 0
                },
                "xp": 0
            }
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
