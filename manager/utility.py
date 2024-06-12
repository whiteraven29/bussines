import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import datetime, timedelta
from django.db.models import Sum
from worker.models import ItemReport,Item
import csv
from django.http import HttpResponse

plt.switch_backend('Agg')

def calculate_profit_loss(branch):
    reports = ItemReport.objects.filter(item__worker__branch=branch)
    total_incomespent = reports.aggregate(Sum('incomespent'))['incomespent__sum'] or 0
    total_incomegained = reports.aggregate(Sum('incomegained'))['incomegained__sum'] or 0
    total_expenditures = reports.aggregate(Sum('expenditures'))['expenditures__sum'] or 0
    
    total_income = total_incomegained - total_incomespent

    if total_income > total_expenditures:
        return 'Profit'
    elif total_income < total_expenditures:
        return 'Loss'
    else:
        return 'Neutral'

def draw_profit_loss_graph(branch, time_period):
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
    dates = [report.date for report in reports]
    income_gained = [report.incomegained for report in reports]
    income_spent = [report.incomespent for report in reports]
    total_income = [gained - spent for gained, spent in zip(income_gained, income_spent)]
    expenditures = [report.expenditures for report in reports]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, total_income, label='Net Income')
    plt.plot(dates, expenditures, label='Expenditures')
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

def get_best_selling_items(branches):
    items = Item.objects.filter(worker__branch__in=branches)
    best_selling_items = []

    for item in items:
        total_sales = sum([report.present for report in item.itemreport_set.all()])
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
            report.present,
            report.consumed,
            report.entered,
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
