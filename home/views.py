from django.shortcuts import render, redirect, HttpResponse
from .forms import ManagerSignupForm, PrivateSignupForm, LoginForm
from manager.models import Manager as ManagerWorker
from private.models import Single as PrivateWorker
from worker.models import Worker as WorkerWorker
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.hashers import make_password


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
            password = form.cleaned_data['password']

            # Check if email is a Gmail address
            if not email.endswith('@gmail.com'):
                form.add_error('email', 'Please use a valid Gmail address')
                return render(request, 'manager_signup.html', {'manager_signup_form': form})

            # Check password requirements
            if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
                form.add_error('password', 'Password must be at least 8 characters long and contain both letters and numbers')
                return render(request, 'manager_signup.html', {'manager_signup_form': form})

            # Check if username or email already exists for manager
            if ManagerWorker.objects.filter(username=username).exists() or ManagerWorker.objects.filter(email=email).exists():
                form.add_error('username', 'Username or email already exists')
                return render(request, 'manager_signup.html', {'manager_signup_form': form})

            # Hash the password
            hashed_password = make_password(password)

            # Create manager user
            manager_user = ManagerWorker.objects.create(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                password=hashed_password  # Save hashed password
            )

            return redirect('home')  # Redirect to login page after successful signup

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
            password = form.cleaned_data['password']

            # Check if email is a Gmail address
            if not email.endswith('@gmail.com'):
                form.add_error('email', 'Please use a valid Gmail address')
                return render(request, 'private_signup.html', {'private_signup_form': form})

            # Check password requirements
            if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
                form.add_error('password', 'Password must be at least 8 characters long and contain both letters and numbers')
                return render(request, 'private_signup.html', {'private_signup_form': form})

            # Check if username or email already exists for private user
            if PrivateWorker.objects.filter(username=username).exists() or PrivateWorker.objects.filter(email=email).exists():
                form.add_error('username', 'Username or email already exists')
                return render(request, 'private_signup.html', {'private_signup_form': form})

            # Hash the password
            hashed_password = make_password(password)

            # Create private user
            private_user = PrivateWorker.objects.create(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                password=hashed_password  # Save hashed password
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
                    if login_type == 'manager':
                        return redirect('/manager/dashboard/')
                    elif login_type == 'worker':
                        return redirect('/worker/worker_dashboard/')
                    elif login_type == 'private':
                        return redirect('/private/private_dashboard/')
                else:
                    return HttpResponse("User is inactive")
            else:
                return HttpResponse("Invalid login")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})