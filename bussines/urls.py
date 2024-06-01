"""
URL configuration for bussines project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home import views as home_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_views.home, name='home'),
    path('manager-signup/', home_views.manager_signup, name='manager_signup'),
    path('private-signup/', home_views.private_signup, name='private_signup'),
    path('about/', home_views.about, name='about'),
    path('services/', home_views.services, name='services'),
    path('accounts/login/', home_views.login_view, name='login_view'),
    path('manager/', include('manager.urls', namespace='manager')),
    path('worker/', include('worker.urls', namespace='worker')),
    path('private/', include('private.urls')),
    
]
