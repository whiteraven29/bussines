from django import forms
from .models import Branch, Worker, DailyReport, Item

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name']

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['firstname', 'lastname', 'branch', 'username', 'password', 'email']

class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReport
        fields = ['laststock', 'present', 'consumed', 'entered', 'remaining', 'incomespent','incomegained', 'expenditures']
