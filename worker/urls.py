from django.urls import path
from . import views

app_name='worker'

urlpatterns = [
    path('worker_dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('register-item', views.register_item, name='register_item'),
    path('fill-report',views.fill_report,name='fill_report'),
    path('daily-expenditure/<int:branch_id>', views.daily_expenditure, name='daily_expenditure'),
    path('update-item/<int:item_id>', views.update_item, name='update_item'),
    path('delete-item/<int:item_id>', views.delete_item, name='delete_item'),
]
