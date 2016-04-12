from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

def skill_export_by_user(user, filter_dashboard):
    from kb.badges.models import UserBadge, Badge
    user_skills = {}
    for user_skill in UserBadge.objects.filter(
            user=user, badge__badge_type=Badge.T_SKILL_BADGE):
        user_skills[user_skill.badge.pk] = user_skill

    if filter_dashboard:
        skills = Badge.objects.filter(
            show_in_dashboard = True, badge_type=Badge.T_SKILL_BADGE
        ).order_by('order')
    else:
        skills = Badge.objects.filter(
            badge_type=Badge.T_SKILL_BADGE).order_by('order')
    skills_export = []
    for skill in skills:
        skill_export = {
            "id": skill.pk,
            "title": skill.title,
            "description": skill.description,
        }
        if skill.pk in user_skills:
            if user_skills[skill.pk].level:
                skill_export["level"] = {
                    "id": user_skills[skill.pk].level.pk,
                    "index": user_skills[skill.pk].level.index
                }
            else:
                skill_export["level"] = {
                    "id": None,
                    "index": 0
                }
            skill_export["xp"] = user_skills[skill.pk].xp
        else:
            skill_export["level"] = { "id": None, "index": 0 }
            skill_export["xp"] = 0
        skills_export.append(skill_export)
    return skills_export

# Create your views here.
def get_skills(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)
    from kb.groups.models import Group, Membership
    filter_dashboard = bool(int(request.GET.get('dashboard', '0')))
    group = request.GET.get('group')
    if group is not None:
        group = get_object_or_404(Group, pk=group)
        if not (request.user.is_superuser or
                request.user.profile.is_teacher(group)):
            return HttpResponse(status=403)

        group_skill_export = []
        for member in Membership.objects.filter(group=group):
            group_skill_export.append({
                'id': member.user.user.pk,
                'role': member.role.role,
                'name': member.user.full_name,
                'skills': skill_export_by_user(member.user, filter_dashboard)
            })
        return JsonResponse({'skills': group_skill_export})
    else:
        skill_export = skill_export_by_user(request.user.profile,
            filter_dashboard)
        return JsonResponse({'skills': skill_export})
