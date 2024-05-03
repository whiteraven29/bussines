from django.urls import path
from . import views

urlpatterns = [
    path('', views.worker_dashboard, name='worker_dashboard'),
    path('register-item', views.register_item, name='register_item'),
    path('update-item <int:item_id>', views.update_item, name='update_item'),
    path('delete-item <int:item_id>', views.delete_item, name='delete_item'),
]
