from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from .models import Branch, Manager
from worker.models import Worker, ItemReport, Item,DailyExpenditure
from .forms import BranchForm
from worker.forms import WorkerForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from .utility import  overall_graph,product_graph,get_best_selling_items,download_report,download_graph
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)




@login_required
def dashboard(request):
    if not isinstance(request.user, Manager):
        return redirect('home')  # Redirect to login if the user is not a manager

    branches = Branch.objects.filter(manager=request.user)
    workers = Worker.objects.filter(branch__in=branches)
    reports = ItemReport.objects.filter(item__worker__branch__in=branches)

    
    
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
    branch = get_object_or_404(Branch, id=branch_id)
    reports = ItemReport.objects.filter(item__worker__branch=branch)
    workers = Worker.objects.filter(branch=branch)  # Fetch workers for the specific branch

    graph = None
    best_selling_items = None

    time_period = request.GET.get('time_period', 'weekly')  # Default to weekly
    graph_type = request.GET.get('graph_type', 'overall')  # Default to overall profit/loss

    if 'view_graph' in request.GET:
        if graph_type == 'overall':
            graph = overall_graph(branch, time_period)
        elif graph_type == 'product':
            graph = product_graph(branch, time_period)
        else:
            graph = None

    if 'generate_best_selling' in request.GET:
        best_selling_items = get_best_selling_items([branch])

    if 'download_report' in request.GET:
        return download_report(reports)

    if 'download_graph' in request.GET and graph:
        return download_graph(graph)

    if 'get_yesterday' in request.GET:
        yesterday = timezone.now().date() - timedelta(days=1)
        reports = reports.filter(date=yesterday)

    summary_data = None
    summary_period = request.GET.get('summary_period', None)
    if summary_period in ['weekly', 'monthly']:
        now = timezone.now().date()
        if summary_period == 'weekly':
            start_date = now - timedelta(weeks=1)
        else:
            start_date = now - timedelta(days=30)

        summarized_reports = reports.filter(date__gte=start_date)
        total_income_spent = summarized_reports.aggregate(Sum('incomespent'))['incomespent__sum'] or 0
        total_income_gained = summarized_reports.aggregate(Sum('incomegained'))['incomegained__sum'] or 0
        total_expenditures = DailyExpenditure.objects.filter(branch=branch, date__gte=start_date).aggregate(Sum('expenditure'))['expenditure__sum'] or 0

        total_income = total_income_gained - total_income_spent
        profit_loss_status = 'Profit' if total_income > total_expenditures else 'Loss' if total_income < total_expenditures else 'Neutral'

        summary_data = {
            'total_income_spent': total_income_spent,
            'total_income_gained': total_income_gained,
            'profit_loss_status': profit_loss_status
        }
    daily_expenditures=DailyExpenditure.objects.filter(branch=branch)    

    return render(request, 'branch_reports.html', {
        'branch': branch,
        'reports': reports,
        'graph': graph,
        'workers': workers,
        'best_selling_items': best_selling_items,
        'time_period': time_period,
        'summary_data': summary_data,
        'summary_period': summary_period,
        'daily_expenditures':daily_expenditures,
    })

@login_required
def delete_branch(request, branch_id):
    branch = Branch.objects.get(id=branch_id)
    if request.method == 'POST':
        branch.delete()
        return redirect('manager:dashboard')
    return render(request, 'delete_branch.html', {'branch': branch})
