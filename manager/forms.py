from django import forms
from .models import Branch, Manager

class ManagerSignupForm(forms.ModelForm):
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

    class Meta:
        model = Manager
        fields = ['firstname', 'lastname', 'email', 'username', 'password']

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name']


