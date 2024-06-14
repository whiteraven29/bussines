from django import forms
from .models import Worker,ItemReport,Item

class WorkerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Worker
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'branch']

class ItemRegistrationForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name']  # Assuming 'name' is the field to be filled by the worker

class ItemForm(forms.ModelForm):
    class Meta:
        model = ItemReport
        fields = ['item', 'laststock', 'present', 'consumed', 'entered', 'remaining', 'incomespent', 'incomegained', 'expenditures']

    def __init__(self, *args, **kwargs):
        worker = kwargs.pop('worker', None)
        super(ItemForm, self).__init__(*args, **kwargs)
        if worker:
            self.fields['item'].queryset = Item.objects.filter(worker=worker)