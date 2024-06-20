import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import datetime, timedelta
from django.db.models import Sum
from worker.models import ItemReport,Item
import csv
from django.http import HttpResponse
from collections import defaultdict
from django.utils import timezone
from worker.models import DailyExpenditure

plt.switch_backend('Agg')



def overall_graph(branch, time_period):
    now = timezone.now()
    if time_period == 'daily':
        start_date = now - timedelta(days=1)
    elif time_period == 'weekly':
        start_date = now - timedelta(weeks=1)
    elif time_period == 'monthly':
        start_date = now - timedelta(days=30)
    elif time_period == 'yearly':
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(weeks=1)  # Default to weekly

    reports = ItemReport.objects.filter(item__worker__branch=branch, date__gte=start_date)
    dates = reports.values_list('date', flat=True).distinct()
    
    daily_expenditures = DailyExpenditure.objects.filter(branch=branch, date__gte=start_date)

    profit_data = []
    for date in dates:
        daily_reports = reports.filter(date=date)
        total_income_gained = daily_reports.aggregate(Sum('incomegained'))['incomegained__sum'] or 0
        total_income_spent = daily_reports.aggregate(Sum('incomespent'))['incomespent__sum'] or 0
        daily_expenditure = daily_expenditures.filter(date=date).first()
        total_expenditure = daily_expenditure.expenditure if daily_expenditure else 0

        net_income = total_income_gained - total_income_spent
        profit_or_loss = net_income - total_expenditure
        profit_data.append((date, profit_or_loss))

    dates, profits_or_losses = zip(*profit_data)

    plt.figure(figsize=(10, 5))
    for i, (date, value) in enumerate(profit_data):
        if value >= 0:
            plt.bar(date, value, color='green', label='Profit' if i == 0 else "")
        else:
            plt.bar(date, value, color='red', label='Loss' if i == 0 else "")

    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title(f'Profit/Loss Trend - {time_period.capitalize()}')
    plt.legend()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode()
    buffer.close()

    return graph

def product_graph(branch, time_period):
    now = datetime.now()
    if time_period == 'daily':
        start_date = now - timedelta(days=1)
    elif time_period == 'weekly':
        start_date = now - timedelta(weeks=1)
    elif time_period == 'monthly':
        start_date = now - timedelta(days=30)
    elif time_period == 'yearly':
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(weeks=1)  # Default to weekly

    reports = ItemReport.objects.filter(item__worker__branch=branch, date__gte=start_date)
    
    # Organize data by item
    data_by_item = defaultdict(list)
    for report in reports:
        profit = report.incomegained - report.incomespent
        data_by_item[report.item.name].append((report.date, profit))
    
    dates = sorted(set(report.date for report in reports))
    
    # Aggregate data by date and item
    aggregated_data = defaultdict(lambda: [0] * len(dates))
    date_index = {date: i for i, date in enumerate(dates)}
    
    for item, data in data_by_item.items():
        for date, profit in data:
            index = date_index[date]
            aggregated_data[item][index] += profit

    plt.figure(figsize=(12, 6))
    
    # Plot data for each item in different colors
    bottom = [0] * len(dates)
    for item, profits in aggregated_data.items():
        plt.bar(dates, profits, bottom=bottom, label=item)
        bottom = [b + p for b, p in zip(bottom, profits)]
        
    plt.xlabel('Date')
    plt.ylabel('Profit')
    plt.title(f'Product-wise Contribution - {time_period.capitalize()}')
    plt.legend()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode()
    buffer.close()
    
    return graph

def get_best_selling_items(branches):
    items = Item.objects.filter(worker__branch__in=branches)
    best_selling_items = []

    for item in items:
        total_sales = sum([report.consumed for report in item.itemreport_set.all()])
        best_selling_items.append((item, total_sales))
    
    best_selling_items.sort(key=lambda x: x[1], reverse=True)
    return best_selling_items[:5]

def download_report(reports):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['Item', 'Worker', 'Branch', 'Date', 'Last Stock', 'Present', 'Consumed', 'Entered', 'Remaining', 'Income Spent', 'Income Gained', 'Expenditures'])

    for report in reports:
        writer.writerow([
            report.item.name,
            report.item.worker.first_name + ' ' + report.item.worker.last_name,
            report.item.worker.branch.name,
            report.date,
            report.laststock,
            report.addedstock,
            report.currentstock,
            report.consumed,
            report.remaining,
            report.incomespent,
            report.incomegained,
            report.expenditures
        ])

    return response

def download_graph(graph):
    # Decode the base64-encoded graph
    image_data = base64.b64decode(graph.encode())

    # Create the HttpResponse object with the appropriate image header
    response = HttpResponse(image_data, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="graph.png"'

    return response
