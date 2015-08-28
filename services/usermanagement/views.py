from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from .forms import *
from .models import Group, Setting, SettingValue, GroupRestriction

def group_defaults(request, setting_id):
    return HttpResponse()

def group_restrictions(request, setting_id):
    return render(request, 'settings/group_restrictions.html',
            {'form': GroupForm(setting_id)})

def user_defaults(request, setting_id):
    return HttpResponse()

def user_restrictions(request, setting_id):
    return HttpResponse()

def group_form(request, setting_id):
    return HttpResponseRedirect(reverse('group_restrictions_select',
            args=[setting_id, request.POST.get('group')]))

def group_restrictions_select(request, setting_id, group_id):
    return render(request, 'settings/group_restrictions_select.html',
            {'form': GroupRestrictForm(setting_id, group_id)})

def restrict_form(request, setting_id, group_id):
    group = Group.objects.get(pk=group_id)
    setting = Setting.objects.get(pk=setting_id)
    for restrict in request.POST.getlist('restrict'):
        val = SettingValue.objects.get(pk=restrict)
        r = GroupRestriction(group=group, settingVal=val, setting=setting)
        r.save()
    return HttpResponseRedirect('http://localhost:8000/admin/')
    
