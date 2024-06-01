from django .urls import path
from . import views

urlpatterns=[
    path('', views.private_dashboard, name='private_dashboard'),
]