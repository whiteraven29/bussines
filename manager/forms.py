from django import forms
from .models import Branch, Manager

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name']

class DateSearchForm(forms.Form):
    date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False)        


