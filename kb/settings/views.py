from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from .models import *
from kb.models import *

from collections import defaultdict
import json

models = {'user': User, 'group': Group,
        'option': GroupRestriction, 'option_user': UserRestriction,
        'value': GroupDefault, 'value_user': UserDefault}

@csrf_exempt
def get_settings(request, setting_id):
    try:
        setting = Setting.objects.get(code=setting_id)
    except (ObjectDoesNotExist, ValueError):
        return HttpResponse(status=400)
    
    #Parse and validate the request parameters
    context = _parse_params(request, setting)
    if context == None:
        return HttpResponse(status=400)
    context['setting'] = setting

    values = {'value': _compute_setting_value(**context)}

    if 'full' in request.GET:
        values['options'] = _compute_setting_options(**context)

    if 'meta' in request.GET:
        values['desc'] = setting.description
        values['single'] = setting.single

    return JsonResponse(values)


def _compute_setting_value(setting, group, user=None):
    #The default value for the user in that context
    if setting.single:
        return _get_setting_default(setting, group, user)
    #The restricted set of values for the in user in that context
    else:
        return _get_setting_list(setting, group, user)

def _compute_setting_options(setting, group, user=None):
    #The set from which a default can be selected
    if setting.single:
        return _get_setting_list(setting, group, user)
    #The restrictions which can be removed to expand the set
    else:
        return _current_restrictions(setting, group, user)

def _get_setting_default(setting, group, user=None):
    value = None

    while group != None:
        #If a user default exists for this group, return that
        if user != None:
            try:
                default = UserDefault.objects.get(user=user, group=group,
                        setting=setting)
                return default.value
            except ObjectDoesNotExist:
                pass

        #Find group-level defaults for settings that have not been set yet
        if value == None:
            try:
                default = GroupDefault.objects.get(group=group, setting=setting)
                value = default.value
            except ObjectDoesNotExist:
                pass

        #Move up to next group in the hierarchy
        group = group.parent

    #If no group level default was found
    if value == None:
        return setting.default.value
    else:
        return value

def _get_setting_list(setting, group, user=None):
    #Retrieve the full value set for the setting
    values = setting.values.all()

    while group != None:
        #Apply user restrictions to the value set, if relevant
        if user != None:
            try:
                restrict = UserRestriction.objects.get(user=user, group=group,
                        setting=setting)
                values = values.exclude(value=restrict.settingVal)
            except ObjectDoesNotExist:
                pass

        #Apply group restrictions to the value set
        try:
            restrict = GroupRestriction.objects.get(group=group, setting=setting)
            values = values.exclude(value=restrict.settingVal)
        except ObjectDoesNotExist:
            pass

        #Move up to next group in the hierarchy
        group = group.parent

    return [elem.value for elem in values]

def _get_current_restrictions(setting, group, user=None):
    if user == None:
        restrict = GroupRestriction.objects.filter(group=group, setting=setting)
    else:
        restrict = GroupRestriction.objects.filter(user=user, group=group, 
                setting=setting)

    return [elem.value for elem in restrict]

@csrf_exempt
def set_settings(request, setting_id, value_id, setting_type):
    if request.method == 'PUT':
        add = True
    elif request.method == 'DELETE':
        add = False
    else:
        return HttpResponse(status=400)

    #Check if the setting and value are a valid combination
    try:
        setting = Setting.objects.get(code=setting_id)
        value = SettingValue.objects.get(value=value_id)
    except (ObjectDoesNotExist, ValueError):
        return HttpResponse(status=400)

    if value.setting != setting or setting_type not in ['option', 'value']:
        return HttpResponse(status=400)

    #Parse and validate the request parameters
    context = _parse_params(request, setting)
    if context == None:
        return HttpResponse(status=400)

    #Add the settings to context to complete the through-model parameters
    context['setting'] = setting
    context['settingVal'] = value

    #Restrictions should be removed on PUT and added on DELETE
    if setting_type == 'option':
        add = not add

    #Distinguish between user and group settings
    if 'user' in context:
        setting_type += '_user'

    #Add or remove the setting
    if add:
        obj, created = models[setting_type].objects.get_or_create(**context)
        if not created:
            return HttpResponse(status=400)
    else:
        try:
            models[setting_type].objects.get(**context).delete()
        except (ObjectDoesNotExist, ValueError):
            return HttpResponse(status=400)

    return HttpResponse(status=201)

def _parse_params(request, setting):
    if 'app-token' in request.GET:
        context = json.loads(request.context)
        if context == None or str(setting.app.pk) != context['app']:
            return None

        del context['app']
    elif 'group' in request.GET:
        context = {'group': request.GET.get('group')}

        if 'user' in request.GET:
            context['user'] = request.GET.get('user')
    else:
        return None

    for key, val in context.items():
        try:
            context[key] = models[key].objects.get(pk=int(val))
        except (ObjectDoesNotExist, ValueError):
            return None

    if 'group' in request.GET and not _user_can_edit_group(request.user.profile, context['group']):
        return None

    if 'user' in context:
        context['user'] = context['user'].profile

    return context

def _user_can_edit_group(profile, group):
    if profile.flat_permissions.filter(code='admin').exists():
        return True
    elif profile.flat_permissions.filter(code='can_edit_group').exists():
        while group != None:
            if Membership.objects.filter(user=profile, group=group, 
                    role__role='teacher').exists():
                return True
            group = group.parent
    return False

