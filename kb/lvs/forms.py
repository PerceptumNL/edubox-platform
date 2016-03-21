from django import forms
from kb.groups.models import Institute, Group

class EdeXmlForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.objects.all())
    edexml = forms.FileField()


class InstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.objects.all())
    first_name = forms.ChoiceField(choices=[
        ('name', 'Name'),
        ('letter', 'First letter'),
        ('initials', 'Initials')])
    prefix = forms.BooleanField()
    separator = forms.CharField(max_length=1)


class CodecultStudentForm(forms.Form):
    group = forms.ModelChoiceField(queryset=
        Group.objects.filter(institute__title='CodeCult'))
    first_name = forms.CharField()
    last_name = forms.CharField()
    password = forms.CharField(required=False)
    email = forms.CharField(required=False)
