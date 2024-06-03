from django.shortcuts import render, redirect
from .models import Worker,Item, ItemReport
from .forms import WorkerForm, ItemForm,ItemRegistrationForm
from django.contrib.auth.decorators import login_required
import logging

logger=logging.getLogger(__name__)


@login_required
def worker_dashboard(request):
    worker = request.user
    reports = ItemReport.objects.filter(item__worker=worker)
    items = Item.objects.all()
    return render(request, 'worker_dashboard.html', {'reports': reports, 'items': items})

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
            item = form.cleaned_data['item']
            laststock = form.cleaned_data['laststock']
            present = form.cleaned_data['present']
            consumed = form.cleaned_data['consumed']
            entered = form.cleaned_data['entered']
            remaining = form.cleaned_data['remaining']
            incomespent = form.cleaned_data['incomespent']
            incomegained = form.cleaned_data['incomegained']
            expenditures = form.cleaned_data['expenditures']
            
            # Check if the item exists
            item, created = Item.objects.get_or_create(name=item)
            # Create ItemReport instance
            report = ItemReport(
                item=item,
                laststock=laststock,
                present=present,
                consumed=consumed,
                entered=entered,
                remaining=remaining,
                incomespent=incomespent,
                incomegained=incomegained,
                expenditures=expenditures,
                
            )
            report.save()

            # Redirect to a success page or do whatever is needed
            return redirect('worker:worker_dashboard')  # Change 'success_page' to the appropriate URL name
    else:
        form = ItemForm()

    return render(request, 'fill_report.html', {'form': form})

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
