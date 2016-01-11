from django import forms
from .models import Institute

class StudentForm(forms.Form):
    students = forms.CharField(widget=forms.Textarea,
        label='Student data (id, first_name, last_name, group)')

class TeacherForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.objects.all(),
        empty_label=None)
    teachers = forms.CharField(widget=forms.Textarea,
        label='Teacher data (id, first_name, last_name, group1; group2; ...)')
