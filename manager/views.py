from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Branch, Manager
from worker.models import Worker, ItemReport, Item
from .forms import BranchForm
from worker.forms import WorkerForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from .utility import calculate_profit_loss, draw_profit_loss_graph,get_best_selling_items,download_report,download_graph
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)




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
            branch_name = form.cleaned_data['name']
            manager = request.user  # Assuming the manager is the logged-in user
            
            # Ensure that the manager exists
            if not Manager.objects.filter(id=manager.id).exists():
                form.add_error(None, 'Associated manager does not exist')
                return render(request, 'register_branch.html', {'form': form})
            
            # Create the branch
            branch = Branch(name=branch_name, manager=manager)
            try:
                branch.save()
                return redirect('manager:dashboard')  # Redirect after successful registration
            except IntegrityError:
                form.add_error(None, 'A foreign key constraint failed. Please check the manager association.')
                return render(request, 'register_branch.html', {'form': form})
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
            
            worker_group, created = Group.objects.get_or_create(name='worker')
            worker.groups.add(worker_group)
            logger.debug(f"Worker {worker.username} registered successfully")
            print(f"Worker {worker.username} registered successfully")


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
    get_yesterday = request.GET.get('get_yesterday', None)
    summary_period = request.GET.get('summary_period', None)

    # Generate graph based on selected time period
    time_period = request.GET.get('time_period', 'weekly')  # Default to weekly
    graph = None
    if 'view_graph' in request.GET:
        branch_id = request.GET.get('branch_id')
        branch = Branch.objects.get(id=branch_id)
        graph = draw_profit_loss_graph(branch, time_period)
        generate_best_selling = request.GET.get('generate_best_selling', None)

    
    
    
    if time_period:
        graph = draw_profit_loss_graph(branch, time_period)

    if generate_best_selling:
        best_selling_items = get_best_selling_items([branch])

    if 'download_report' in request.GET:
        return download_report(reports)   

    if request.GET.get('download_graph'):
        if graph:
            return download_graph(graph) 
        
    if get_yesterday:
        yesterday = timezone.now().date() - timedelta(days=1)
        reports = reports.filter(date=yesterday)  

    summary_data = None
    if summary_period in ['weekly', 'monthly']:
        now = timezone.now().date()
        if summary_period == 'weekly':
            start_date = now - timedelta(weeks=1)
        else:
            start_date = now - timedelta(days=30)

        summarized_reports = reports.filter(date__gte=start_date)
        total_income_spent = summarized_reports.aggregate(Sum('incomespent'))['incomespent__sum'] or 0
        total_income_gained = summarized_reports.aggregate(Sum('incomegained'))['incomegained__sum'] or 0
        total_expenditures = summarized_reports.aggregate(Sum('expenditures'))['expenditures__sum'] or 0
        
        total_income = total_income_gained - total_income_spent
        if total_income > total_expenditures:
            profit_loss_status = 'Profit'
        elif total_income < total_expenditures:
            profit_loss_status = 'Loss'
        else:
            profit_loss_status = 'Neutral'
        
        summary_data = {
            'total_income_spent': total_income_spent,
            'total_income_gained': total_income_gained,
            'profit_loss_status': profit_loss_status
        }
   
        
        

    return render(request, 'branch_reports.html', {
        'branch': branch,
        'reports': reports,
        'graph': graph,
        'workers': workers,
        'best_selling_items': best_selling_items,
        'time_period': time_period,
        'summary_data':summary_data,
        'summary_period':summary_period
    })

