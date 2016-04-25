from django import forms
from kb.groups.models import Institute, Group

class EdeXmlForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.objects.all())
    edexml = forms.FileField()


class InstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.objects.all())
    email_generation = forms.ChoiceField(choices=[
        ('none', 'Do not generate'),
        ('name', 'Name'),
        ('letter', 'First letter'),
        ('initials', 'Initials')])
    prefix = forms.BooleanField(required=False)
    separator = forms.CharField(max_length=1, required=False)

class EmailForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.CharField(required=False)

class GroupForm(forms.Form):
    group = forms.CharField(required=False)
    create = forms.ChoiceField(choices=[
        ('no', 'Leave group as is'),
        ('import', 'Import from EdeXML')],
        widget=forms.RadioSelect())

class CodecultStudentForm(forms.Form):
    group = forms.ModelChoiceField(queryset=
        Group.objects.filter(institute__title='CodeCult'))
    first_name = forms.CharField()
    last_name_prefix = forms.CharField(required=False)
    last_name = forms.CharField()
    password = forms.CharField(required=False)
    email = forms.CharField(required=False)

class PasswordForm(forms.Form):
    password = forms.CharField(required=False)
