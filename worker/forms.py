from django import forms
from .models import Worker,ItemReport,Item

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['branch', 'username', 'password']

class ItemRegistrationForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name']  # Assuming 'name' is the field to be filled by the worker

class ItemForm(forms.ModelForm):
    class Meta:
        model = ItemReport
        fields = ['item','laststock', 'present', 'consumed', 'entered', 'remaining', 'incomespent','incomegained', 'expenditures']
