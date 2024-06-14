from django.shortcuts import render, redirect, get_object_or_404
from .models import Worker,Item, ItemReport
from .forms import  ItemForm,ItemRegistrationForm
from django.contrib.auth.decorators import login_required
import logging
from django.utils import timezone
from datetime import timedelta

logger=logging.getLogger(__name__)


@login_required
def worker_dashboard(request):
    worker = request.user
    items = Item.objects.filter(worker=worker)  # Filter items by the logged-in worker
    reports=ItemReport.objects.filter(item__worker=worker)
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
        today = timezone.now().date()
        daily_reports = ItemReport.objects.filter(item__worker=worker, date=today)

    return render(request, 'worker_dashboard.html', {
        'reports':reports,
        'items': items,
        'latest_reports': latest_reports,
        'daily_reports': daily_reports
    })

@login_required
def register_item(request):
    if request.method == 'POST':
        form = ItemRegistrationForm(request.POST)
        if form.is_valid():
            user = request.user
            logger.debug(f"User ID: {user.id}, Username: {user.username}")
            logger.debug(f"User Groups: {[group.name for group in user.groups.all()]}")

            try:
                worker = Worker.objects.get(id=user.id)
            except Worker.DoesNotExist:
                logger.error(f"Worker with user ID {user.id} does not exist.")
                return render(request, 'error.html', {'message': 'You are not a registered worker.'})

            if not user.groups.filter(name='worker').exists():
                logger.error(f"User ID {user.id} is not in the 'worker' group.")
                return render(request, 'error.html', {'message': 'You are not authorized to register items.'})

            item = form.save(commit=False)
            item.worker = worker
            item.save()
            return redirect('worker:worker_dashboard')
    else:
        form = ItemRegistrationForm()

    return render(request, 'register_item.html', {'form': form})

@login_required
def fill_report(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.item.worker = request.user  # Assign the item's worker as the logged-in user
            report.save()
            return redirect('worker:worker_dashboard')
    else:
        # Filter items based on the logged-in worker
        items = Item.objects.filter(worker=request.user)

        item_id = request.GET.get('item_id')
        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            last_report = ItemReport.objects.filter(item=item).order_by('-date').first()
            reports = ItemReport.objects.filter(item=item).order_by('-date')
        else:
            item = None
            last_report = None
            reports = None

        form = ItemForm(initial={'item': item}, worker=request.user)  # Pass the worker to the form

    return render(request, 'fill_report.html', {'form': form, 'items': items, 'last_report': last_report, 'reports': reports})

@login_required
def update_item(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('worker_dashboard')
    else:
        form = ItemForm(instance=item)
    return render(request, 'update_item.html', {'form': form, 'item': item})

@login_required
def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('worker_dashboard')
    return render(request, 'delete_item.html', {'item': item})
