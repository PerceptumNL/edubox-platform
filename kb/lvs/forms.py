from django import forms
from kb.groups.models import Institute, Group

class EdeXmlForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.objects.all())
    edexml = forms.FileField()
    password = forms.CharField(required=False)
    teacher_emails = forms.CharField(widget=forms.Textarea, required=False)

class CodecultStudentForm(forms.Form):
    group = forms.ModelChoiceField(queryset=
        Group.objects.filter(institute__title='CodeCult'))
    first_name = forms.CharField()
    last_name = forms.CharField()
    password = forms.CharField(required=False)
    email = forms.CharField(required=False)
