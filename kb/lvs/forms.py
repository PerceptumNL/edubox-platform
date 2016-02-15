from django import forms
from kb.groups.models import Institute

class EdeXmlForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.objects.all())
    edexml = forms.FileField()
    password = forms.CharField(required=False)
