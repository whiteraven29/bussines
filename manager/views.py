from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Branch, Manager
from worker.models import Worker, ItemReport, Item
from .forms import BranchForm, ManagerSignupForm
from worker.forms import WorkerForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from .utility import calculate_profit_loss, draw_profit_loss_graph,get_best_selling_items,download_report,download_graph
from datetime import datetime, timedelta
from django.utils import timezone




@login_required
def dashboard(request):
    if not isinstance(request.user, Manager):
        return redirect('login')  # Redirect to login if the user is not a manager

    branches = Branch.objects.filter(manager=request.user)
    workers = Worker.objects.filter(branch__in=branches)
    reports = ItemReport.objects.filter(item__worker__branch__in=branches)

    for branch in branches:
        branch.profit_loss = calculate_profit_loss(branch)

    
    # Filter reports by date if requested
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
        reports = reports.filter(date=selected_date)
    else:
        selected_date = timezone.now().date()


    return render(request, 'dashboard.html', {
        'branches': branches,
        'workers': workers,
        'reports': reports,
        'selected_date': selected_date,
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

    # Generate graph based on selected time period
    time_period = request.GET.get('time_period', 'weekly')  # Default to weekly
    graph = None
    if 'view_graph' in request.GET:
        branch_id = request.GET.get('branch_id')
        branch = Branch.objects.get(id=branch_id)
        graph = draw_profit_loss_graph(branch, time_period)

    
    
    
    if time_period:
        graph = draw_profit_loss_graph(branch, time_period)

    if generate_best_selling:
        best_selling_items = get_best_selling_items([branch])

    if 'download_report' in request.GET:
        return download_report(reports)   

    if request.GET.get('download_graph'):
        if graph:
            return download_graph(graph) 

    return render(request, 'branch_reports.html', {
        'branch': branch,
        'reports': reports,
        'graph': graph,
        'workers': workers,
        'best_selling_items': best_selling_items,
        'time_period': time_period
    })

