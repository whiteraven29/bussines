from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Branch, Manager
from worker.models import Worker, ItemReport, Item
from .forms import BranchForm, ManagerSignupForm
from worker.forms import WorkerForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from django.contrib.auth.models import Group
from datetime import datetime, timedelta

plt.switch_backend('Agg')

@login_required
def dashboard(request):
    if not isinstance(request.user, Manager):
        return redirect('login')  # Redirect to login if the user is not a manager

    branches = Branch.objects.filter(manager=request.user)
    workers = Worker.objects.filter(branch__in=branches)
    reports = ItemReport.objects.filter(item__worker__branch__in=branches)

    for branch in branches:
        branch.profit_loss = calculate_profit_loss(branch)

    return render(request, 'dashboard.html', {
        'branches': branches,
        'workers': workers,
        'reports': reports
    })

@login_required
def register_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save(commit=False)
            branch.manager = request.user  # Ensure this is a Manager instance
            branch.save()
            return redirect('manager:dashboard')
    else:
        form = BranchForm()
    return render(request, 'register_branch.html', {'form': form})

@login_required
def register_worker(request):
    if request.method == 'POST':
        form = WorkerForm(request.POST)
        if form.is_valid():
            worker = form.save(commit=False)
            password = form.cleaned_data['password']
            worker.set_password(password)  # Hash the password
            worker.save()
            
            worker_group = Group.objects.get(name='worker')
            worker.groups.add(worker_group)

            return redirect('manager:dashboard')
    else:
        form = WorkerForm()
    return render(request, 'register_worker.html', {'form': form})

@login_required
def unregister_worker(request, worker_id):
    worker = Worker.objects.get(id=worker_id)
    if request.method == 'POST':
        worker.delete()
        return redirect('manager:dashboard')
    return render(request, 'unregister_worker.html', {'worker': worker})

@login_required
def branch_reports(request, branch_id):
    branch = Branch.objects.get(id=branch_id)
    reports = ItemReport.objects.filter(item__worker__branch=branch)
    workers = Worker.objects.filter(branch=branch)  # Fetch workers for the specific branch


    graph = None
    best_selling_items = None
    
    time_period = request.GET.get('time_period', None)
    generate_best_selling = request.GET.get('generate_best_selling', None)
    
    if time_period:
        graph = draw_profit_loss_graph(branch, time_period)

    if generate_best_selling:
        best_selling_items = get_best_selling_items([branch])

    return render(request, 'branch_reports.html', {
        'branch': branch,
        'reports': reports,
        'graph': graph,
        'workers': workers,
        'best_selling_items': best_selling_items,
        'time_period': time_period
    })

def calculate_profit_loss(branch):
    reports = ItemReport.objects.filter(item__worker__branch=branch)
    total_incomespent = reports.aggregate(Sum('incomespent'))['incomespent__sum'] or 0
    total_incomegained = reports.aggregate(Sum('incomegained'))['incomegained__sum'] or 0
    total_expenditures = reports.aggregate(Sum('expenditures'))['expenditures__sum'] or 0
    
    total_income = total_incomegained - total_incomespent

    if total_income > total_expenditures:
        return 'Profit'
    elif total_income < total_expenditures:
        return 'Loss'
    else:
        return 'Neutral'

def draw_profit_loss_graph(branch, time_period):
    now = datetime.now()
    if time_period == 'daily':
        start_date = now - timedelta(days=1)
    elif time_period == 'weekly':
        start_date = now - timedelta(weeks=1)
    elif time_period == 'monthly':
        start_date = now - timedelta(days=30)
    elif time_period == 'yearly':
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(weeks=1)  # Default to weekly

    reports = ItemReport.objects.filter(item__worker__branch=branch, date__gte=start_date)
    dates = [report.date for report in reports]
    income_gained = [report.incomegained for report in reports]
    income_spent = [report.incomespent for report in reports]
    total_income = [gained - spent for gained, spent in zip(income_gained, income_spent)]
    expenditures = [report.expenditures for report in reports]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, total_income, label='Net Income')
    plt.plot(dates, expenditures, label='Expenditures')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title(f'Profit/Loss Trend - {time_period.capitalize()}')
    plt.legend()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode()
    buffer.close()

    return graph

def get_best_selling_items(branches):
    items = Item.objects.filter(worker__branch__in=branches)
    best_selling_items = []

    for item in items:
        total_sales = sum([report.present for report in item.itemreport_set.all()])
        best_selling_items.append((item, total_sales))
    
    best_selling_items.sort(key=lambda x: x[1], reverse=True)
    return best_selling_items[:5]
