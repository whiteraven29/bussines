from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Branch, Manager
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from .forms import BranchForm,ManagerSignupForm
from worker.models import Worker, ItemReport, Item
from worker.forms import WorkerForm



def manager_signup(request):
    if request.method == 'POST':
        form = ManagerSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to manager dashboard after signup
    else:
        form = ManagerSignupForm()
    return render(request, 'manager_signup.html', {'form': form})

def register_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save()
            return redirect('dashboard')
    else:
        form = BranchForm()
    return render(request, 'register_branch.html', {'form': form})

def register_worker(request):
    if request.method == 'POST':
        form = WorkerForm(request.POST)
        if form.is_valid():
            worker = form.save()
            return redirect('dashboard')
    else:
        form = WorkerForm()
    return render(request, 'register_worker.html', {'form': form})


def unregister_worker(request, worker_id):
    worker = Worker.objects.get(id=worker_id)
    if request.method == 'POST':
        worker.delete()
        return redirect('dashboard')
    return render(request, 'unregister_worker.html', {'worker': worker})

def dashboard(request):
    branches = Branch.objects.all()
    workers = Worker.objects.all()
    reports = ItemReport.objects.all()

    for branch in branches:
        branch.profit_loss = calculate_profit_loss(branch)
        branch.graph = draw_profit_loss_graph(branch)

    best_selling_items = get_best_selling_items()

    return render(request, 'dashboard.html', {'branches': branches, 'workers': workers, 'reports': reports, 'best_selling_items': best_selling_items})

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

    if total_income >total_expenditures:
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
    total_income = [report.income for report in reports]  # Difference between income_gained and income_spent
    expenditures = [report.expenditures for report in reports]

    plt.plot(dates, total_income, label='Net Income')
    plt.plot(dates, expenditures, label='Expenditures')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title('Profit/Loss Trend')
    plt.legend()

    # Convert the graph to base64 for embedding in HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode()
    buffer.close()

    return graph

def get_best_selling_items():
    items = Item.objects.all()
    best_selling_items = []
    # Example: assume best selling items are the ones with highest sales
    for item in items:
        total_sales = sum([report.present for report in item.Itemreport_set.all()])
        best_selling_items.append((item, total_sales))
    best_selling_items.sort(key=lambda x: x[1], reverse=True)
    return best_selling_items[:5]  # Return top 5 best selling items
