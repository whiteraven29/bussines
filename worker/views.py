from django.shortcuts import render, redirect, get_object_or_404
from .models import Worker,Item, ItemReport
from .forms import  ItemForm,ItemRegistrationForm,ItemUpdateForm, DailyExpenditureForm
from django.contrib.auth.decorators import login_required
import logging
from django.utils import timezone
from django.http import HttpResponse
from django.forms import modelformset_factory
from manager.models import Branch

logger=logging.getLogger(__name__)


@login_required
def worker_dashboard(request):
    worker = request.user
    if not isinstance(worker, Worker):
        logger.error("Current user is not a worker: %s", worker)
        return HttpResponse("User is not a worker")
    items = Item.objects.filter(worker=worker)  # Filter items by the logged-in worker
    reports=ItemReport.objects.filter(item__worker=worker)
    branch=worker.branch
    latest_reports = []
    daily_reports = []

    if 'latest_reports' in request.GET:
        for item in items:
            try:
                latest_report = ItemReport.objects.filter(item=item).latest('date')
                latest_reports.append(latest_report)
            except ItemReport.DoesNotExist:
                continue  # Skip if no report exists for this item

    if 'daily_reports' in request.GET:
        daily_reports = ItemReport.objects.filter(item__worker=worker).order_by('-date')
    else:
        daily_reports = None

    return render(request, 'worker_dashboard.html', {
        'reports':reports,
        'items': items,
        'latest_reports': latest_reports,
        'daily_reports': daily_reports,
        'branch':branch
    })

@login_required
def register_item(request):
    ItemFormSet = modelformset_factory(Item, form=ItemRegistrationForm, extra=1)
    if request.method == 'POST':
        formset = ItemFormSet(request.POST, queryset=Item.objects.none())
        if formset.is_valid():
            for form in formset:
                item = form.save(commit=False)
                item.worker = request.user
                item.save()
            return redirect('worker:worker_dashboard')
    else:
        formset = ItemFormSet(queryset=Item.objects.none())
    
    return render(request, 'register_item.html', {'formset': formset})

@login_required
def fill_report(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.item.worker = request.user  # Assign the item's worker as the logged-in user
            report.date=timezone.now()
            report.save()
            return redirect('worker:fill_report')
    else:
        # Filter items based on the logged-in worker
        items = Item.objects.filter(worker=request.user)

        item_id = request.GET.get('item_id')
        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            last_report = ItemReport.objects.filter(item=item).order_by('-date').first()
            reports = ItemReport.objects.filter(item=item).order_by('-date')
            
            if last_report:
                # Initialize the form with the last report's remaining value as laststock
                form = ItemForm(initial={'item': item, 'laststock': last_report.remaining})
            else:
                form = ItemForm(initial={'item': item})
        else:
            item = None
            last_report = None
            reports = None
            form = ItemForm()  # Initialize form without specific item

    return render(request, 'fill_report.html', {'form': form, 'items': items, 'last_report': last_report, 'reports': reports})

@login_required
def daily_expenditure(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'POST':
        form = DailyExpenditureForm(request.POST)
        if form.is_valid():
            daily_expenditure = form.save(commit=False)
            daily_expenditure.branch = branch
            daily_expenditure.save()
            return redirect('worker:worker_dashboard')
    else:
        form = DailyExpenditureForm()

    return render(request, 'daily_expenditure.html', {'form': form, 'branch': branch})

@login_required
def update_item(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        form = ItemUpdateForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('worker:worker_dashboard')
    else:
        form = ItemUpdateForm(instance=item)
    return render(request, 'update_item.html', {'form': form, 'item': item})

@login_required
def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('worker:worker_dashboard')
    return render(request, 'delete_item.html', {'item': item})
