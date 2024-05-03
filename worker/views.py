from django.shortcuts import render, redirect
from .models import Worker,Item, ItemReport
from .forms import WorkerForm, ItemForm


def worker_dashboard(request):
    worker = Worker.objects.get(id=1)  # Get worker based on session or authentication
    reports = ItemReport.objects.filter(worker=worker)
    items = Item.objects.all()

    return render(request, 'worker_dashboard.html', {'reports': reports, 'items': items})

def worker_dashboard(request):
    worker = Worker.objects.get(id=1)  # Get worker based on session or authentication
    reports = ItemReport.objects.filter(worker=worker)
    items = Item.objects.filter(worker=worker)
    return render(request, 'worker_dashboard.html', {'reports': reports, 'items': items})

def register_item(request):
    worker = Worker.objects.get(id=1)  # Get worker based on session or authentication
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.worker = worker
            item.save()
            return redirect('worker_dashboard')
    else:
        form = ItemForm()
    return render(request, 'register_item.html', {'form': form})

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

def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('worker_dashboard')
    return render(request, 'delete_item.html', {'item': item})
