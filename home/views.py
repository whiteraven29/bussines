from django.shortcuts import render, redirect
from .forms import ManagerSignupForm, PrivateSignupForm, LoginForm
from manager.models import Manager as ManagerWorker
from private.models import Single as PrivateWorker
from worker.models import Worker as WorkerWorker

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

            # Create manager user
            manager_user = ManagerWorker.objects.create(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                password=password
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

            # Create private user
            private_user = PrivateWorker.objects.create(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                password=password
            )

            return redirect('home')  # Redirect to login page after successful signup

    else:
        form = PrivateSignupForm()

    return render(request, 'private_signup.html', {'private_signup_form': form})

from django.shortcuts import render, redirect
from .forms import LoginForm
from worker.models import Worker

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_username = form.cleaned_data['login_username']
            login_password = form.cleaned_data['login_password']
            login_type = form.cleaned_data['login_type']

            # Implement your login logic here
            if login_type == 'manager':
                # Check manager credentials
                try:
                    manager_worker = ManagerWorker.objects.get(username=login_username, password=login_password)
                    # Redirect to manager dashboard
                    return redirect('dashboard')
                except ManagerWorker.DoesNotExist:
                    pass  # Manager credentials not found
            elif login_type == 'worker':
                # Check worker credentials
                try:
                    # Query Worker by username (assuming username is branch name) and password
                    worker_worker = Worker.objects.get(branch__name=login_username, password=login_password)
                    # Redirect to worker dashboard
                    return redirect('worker_dashboard')
                except Worker.DoesNotExist:
                    pass  # Worker credentials not found
            elif login_type == 'private':
                # Check private user credentials
                try:
                    private_worker = PrivateWorker.objects.get(username=login_username, password=login_password)
                    # Redirect to private dashboard
                    return redirect('private_dashboard')
                except PrivateWorker.DoesNotExist:
                    pass  # Private user credentials not found

    else:
        # If it's not a POST request, create an empty form
        form = LoginForm()

    # Render the login page with the form
    return render(request, 'login.html', {'form': form})
