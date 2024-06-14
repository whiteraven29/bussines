from django.shortcuts import render, redirect, HttpResponse
from .forms import ManagerSignupForm, PrivateSignupForm, LoginForm
from manager.models import Manager as ManagerWorker
from private.models import Single as PrivateWorker
from worker.models import Worker as WorkerWorker
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')


def manager_signup(request):
    if request.method == 'POST':
        form = ManagerSignupForm(request.POST)
        if form.is_valid():
            # Extract form data
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            
            # Check if username or email already exists for manager
            if ManagerWorker.objects.filter(username=username).exists():
                form.add_error('username', 'Username already exists')
                return render(request, 'manager_signup.html', {'manager_signup_form': form})
            if ManagerWorker.objects.filter(email=email).exists():
                form.add_error('email', 'Email already exists')
                return render(request, 'manager_signup.html', {'manager_signup_form': form})

            # Hash the password
            hashed_password = make_password(password1)

            # Create manager user
            manager_user = ManagerWorker.objects.create(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                password=hashed_password  # Save hashed password
                
            )

            return redirect('manager:dashboard')  # Redirect to login page after successful signup
    else:
        form = ManagerSignupForm()

    return render(request, 'manager_signup.html', {'manager_signup_form': form})

def private_signup(request):
    if request.method == 'POST':
        form = PrivateSignupForm(request.POST)
        if form.is_valid():
            # Extract form data
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1= form.cleaned_data['password1']
            

            # Check if username or email already exists for manager
            if PrivateWorker.objects.filter(username=username).exists():
                form.add_error('username', 'Username already exists')
                return render(request, 'manager_signup.html', {'manager_signup_form': form})
            if PrivateWorker.objects.filter(email=email).exists():
                form.add_error('email', 'Email already exists')
                return render(request, 'manager_signup.html', {'manager_signup_form': form})

            # Hash the password
            hashed_password = make_password(password1)

            # Create private user
            private_user = PrivateWorker.objects.create(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                password1=hashed_password  # Save hashed password
                
            )

            return redirect('private_dashboard')  # Redirect to login page after successful signup
    else:
        form = PrivateSignupForm()

    return render(request, 'private_signup.html', {'private_signup_form': form})

# views.py

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_username = form.cleaned_data['login_username']
            login_password = form.cleaned_data['login_password']
            login_type = form.cleaned_data['login_type']

            user = authenticate(request, username=login_username, password=login_password)

            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    logger.debug(f"User {user.username} logged in successfully as {login_type}")
                    if login_type == 'manager':
                        return redirect('/manager/dashboard/')
                    elif login_type == 'worker':
                        return redirect('/worker/worker_dashboard/')
                    elif login_type == 'private':
                        return redirect('/private/private_dashboard/')
                else:
                    logger.debug("User is inactive")
                    return HttpResponse("User is inactive")
            else:
                logger.debug("Invalid login")
                return HttpResponse("Invalid login")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})