from django.shortcuts import render, redirect
from .models import Worker,Item, ItemReport
from .forms import WorkerForm, ItemForm,ItemRegistrationForm
from django.contrib.auth.decorators import login_required


@login_required
def worker_dashboard(request):
    worker = request.user.worker
    reports = ItemReport.objects.filter(item__worker=worker)
    items = Item.objects.all()
    return render(request, 'worker:worker_dashboard.html', {'reports': reports, 'items': items})

@login_required
def register_item(request):
    if request.method == 'POST':
        form = ItemRegistrationForm(request.POST)
        if form.is_valid():
            # Get the current logged-in user
            user = request.user
            # Check if the user is a worker
            if user.groups.filter(name='worker').exists():
                # Get the worker associated with the user
                worker = user.worker
                # Associate the item with the worker
                item = form.save(commit=False)
                item.worker = worker
                item.save()
                return redirect('worker:worker_dashboard')
            else:
                # If user is not a worker, redirect to error page
                return render(request, 'error.html', {'message': 'You are not authorized to register items.'})
    else:
        form = ItemRegistrationForm()

    return render(request, 'worker:register_item.html', {'form': form})

@login_required
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
            return redirect('worker:worker_dashboard')  # Change 'success_page' to the appropriate URL name
    else:
        form = ItemForm()

    return render(request, 'worker:fill_report.html', {'form': form})

@login_required
def update_item(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('worker:worker_dashboard')
    else:
        form = ItemForm(instance=item)
    return render(request, 'worker:update_item.html', {'form': form, 'item': item})

@login_required
def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('worker:worker_dashboard')
    return render(request, 'worker:delete_item.html', {'item': item})
