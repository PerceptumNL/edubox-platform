from django import forms

from .models import Setting, Group, GroupRestriction

class GroupForm(forms.Form):
    def __init__(self, setting_id, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        app = Setting.objects.get(pk=setting_id).app
        if app == None:
            queryset = Group.objects.all()
        else:
            queryset = Group.objects.filter(apps=app)
        self.fields['group'] = forms.ModelChoiceField(queryset=queryset)

class GroupRestrictForm(forms.Form):
    def __init__(self, setting_id, group_id, *args, **kwargs):
        super(GroupRestrictForm, self).__init__(*args, **kwargs)
        values = Setting.objects.get(pk=setting_id).values.all()
        group = Group.objects.get(pk=group_id)
        while group != None:
            for restrict in GroupRestriction.objects.filter(setting=setting_id,
                    group=group.pk):
                values = values.exclude(pk=restrict.settingVal.pk)
            group = group.parent
        self.fields['restrict'] = forms.ModelMultipleChoiceField(queryset=values)

