from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('manager-signup', views.manager_signup, name='manager_signup'),
    path('private-signup', views.private_signup, name='private_signup'),
    path('login', views.login, name='login'),
    path('about', views.about, name='about'),
    path('services', views.services, name='services'),
]
