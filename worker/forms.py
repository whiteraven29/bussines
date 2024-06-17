from django import forms
from .models import Worker,ItemReport,Item, DailyExpenditure
from django.forms import modelformset_factory

class WorkerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Worker
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'branch']

class ItemRegistrationForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name']  # Assuming 'name' is the field to be filled by the worker

ItemFormSet= modelformset_factory(Item, form=ItemRegistrationForm, extra=1)    

class ItemForm(forms.ModelForm):
    class Meta:
        model = ItemReport
        fields = ['item', 'laststock', 'addedstock', 'currentstock', 'consumed', 'remaining', 'incomespent', 'incomegained']

class ItemUpdateForm(forms.ModelForm):
    class Meta:
        model = ItemReport
        fields = [ 'laststock', 'addedstock', 'currentstock', 'consumed', 'remaining', 'incomespent', 'incomegained']     

    def __init__(self, *args, **kwargs):
        worker = kwargs.pop('worker', None)
        super().__init__(*args, **kwargs)
        if worker:
            self.fields['item'].queryset = Item.objects.filter(worker=worker)

class DailyExpenditureForm(forms.ModelForm):
    class Meta:
        model = DailyExpenditure
        fields = ['date', 'expenditure']            