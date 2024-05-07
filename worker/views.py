from django.shortcuts import render, redirect
from .models import Worker,Item, ItemReport
from .forms import WorkerForm, ItemForm,ItemRegistrationForm


def worker_dashboard(request):
    worker = Worker.objects.get(id=1)  # Get worker based on session or authentication
    reports = ItemReport.objects.filter(item__worker=worker)
    items = Item.objects.all()

    return render(request, 'worker_dashboard.html', {'reports': reports, 'items': items})

def register_item(request):
    if request.method == 'POST':
        form = ItemRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to worker dashboard after item registration
    else:
        form = ItemRegistrationForm()

    return render(request, 'register_item.html', {'form': form})


def fill_report(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item_name = form.cleaned_data['item_name']
            last_stock = form.cleaned_data['last_stock']
            present = form.cleaned_data['present']
            consumed = form.cleaned_data['consumed']
            entered = form.cleaned_data['entered']
            remaining = form.cleaned_data['remaining']
            incomespent = form.cleaned_data['incomespent']
            incomegained = form.cleaned_data['incomegained']
            expenditures = form.cleaned_data['expenditures']
            date = form.cleaned_data['date']

            # Check if the item exists
            item, created = Item.objects.get_or_create(name=item_name)

            # Create ItemReport instance
            report = ItemReport(
                item=item,
                laststock=last_stock,
                present=present,
                consumed=consumed,
                entered=entered,
                remaining=remaining,
                incomespent=incomespent,
                incomegained=incomegained,
                expenditures=expenditures,
                date=date
            )
            report.save()

            # Redirect to a success page or do whatever is needed
            return redirect('worker_dashboard')  # Change 'success_page' to the appropriate URL name
    else:
        form = ItemForm()

    return render(request, 'fill_report.html', {'form': form})

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
