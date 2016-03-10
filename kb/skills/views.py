from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

def skill_export_by_user(user):
    from kb.badges.models import UserBadge, Badge
    user_skills = {}
    for user_skill in UserBadge.objects.filter(
            user=user, badge__badge_type=Badge.T_SKILL_BADGE):
        user_skills[user_skill.badge.pk] = user_skill

    skills = Badge.objects.filter(
        badge_type=Badge.T_SKILL_BADGE).order_by('order')
    skill_export = {}
    for skill in skills:
        skill_export[skill.pk] = {
            "id": skill.pk,
            "title": skill.title,
            "description": skill.description,
        }
        if skill.pk in user_skills:
            if user_skills[skill.pk].level:
                skill_export[skill.pk]["level"] = {
                    "id": user_skill[skill.pk].level.pk,
                    "index": user_skill[skill.pk].level.index
                },
            else:
                skill_export[skill.pk]["level"] = {
                    "id": None,
                    "index": 0
                }
            skill_export[skill.pk]["xp"] = user_skills[skill.pk].xp
        else:
            skill_export[skill.pk]["level"] = { "id": None, "index": 0 }
            skill_export[skill.pk]["xp"] = 0
    return skill_export

# Create your views here.
def get_skills(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)
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
