from django.urls import path
from . import views

urlpatterns = [
    path('', views.manager_dashboard, name='manager_dashboard'),
    path('register-branch', views.register_branch, name='register_branch'),
    path('register-worker', views.register_worker, name='register_worker'),
    path('unregister-worker <int:worker_id>', views.unregister_worker, name='unregister_worker'),
    path('branch-reports <int:branch_id>', views.branch_reports, name='branch_reports'),
]
