from django.urls import path
from . import views
from home import views as home_views

app_name='manager'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('home/',home_views.home, name='home'),
    path('register-branch', views.register_branch, name='register_branch'),
    path('register-worker', views.register_worker, name='register_worker'),
    path('unregister-worker/<int:worker_id>', views.unregister_worker, name='unregister_worker'),
    path('branch-reports/<int:branch_id>', views.branch_reports, name='branch_reports'),
    path('delete-branch/<int:branch_id>', views.delete_branch, name='delete_branch'),
]
