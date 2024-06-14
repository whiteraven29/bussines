from django import forms
from .models import Branch, Manager

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name']


