
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

@login_required
def dashboard(request):
    # Ensure request.user is a Manager instance
    if not isinstance(request.user, Manager):
        return redirect('login')  # Redirect to login if the user is not a manager

    branches = Branch.objects.filter(manager=request.user)
    workers = Worker.objects.filter(branch__in=branches)
    reports = ItemReport.objects.filter(item__worker__branch__in=branches)
    best_selling_items = get_best_selling_items(branches)

    for branch in branches:
        branch.profit_loss = calculate_profit_loss(branch)
        branch.graph = draw_profit_loss_graph(branch)

    return render(request, 'dashboard.html', {'branches': branches, 'workers': workers, 'reports': reports, 'best_selling_items': best_selling_items})

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
            # Hash the password
            worker.set_password(password)
            worker.save()
            
            # Assign the user to the 'worker' group
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
    return render(request, 'branch_reports.html', {'branch': branch, 'reports': reports})

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

def draw_profit_loss_graph(branch):
    reports = ItemReport.objects.filter(item__worker__branch=branch)
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
    plt.title('Profit/Loss Trend')
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
