from django import forms
from .models import Worker,ItemReport

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['firstname', 'lastname', 'branch', 'username', 'password', 'email']

class ItemForm(forms.ModelForm):
    class Meta:
        model = ItemReport
        fields = ['laststock', 'present', 'consumed', 'entered', 'remaining', 'incomespent','incomegained', 'expenditures']
