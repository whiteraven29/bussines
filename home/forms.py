from django import forms
from manager.models import Manager
from django.contrib.auth.forms import UserCreationForm


class ManagerSignupForm(UserCreationForm):
    class Meta:
        model = Manager
        fields = ['firstname', 'lastname', 'email', 'username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Please use a valid Gmail address")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            raise forms.ValidationError("Password must be at least 8 characters long and contain both letters and numbers")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

class PrivateSignupForm(forms.Form):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)
    username = forms.CharField(max_length=100)
    email = forms.EmailField(label="Email")
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Please use a valid Gmail address")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            raise forms.ValidationError("Password must be at least 8 characters long and contain both letters and numbers")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")


class LoginForm(forms.Form):
    login_username = forms.CharField(max_length=100)
    login_password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    login_type = forms.ChoiceField(choices=[('manager', 'Manager'), ('private', 'Private'), ('worker', 'Worker')])

    def clean(self):
        cleaned_data = super().clean()
        login_username = cleaned_data.get("login_username")
        login_password = cleaned_data.get("login_password")
        login_type = cleaned_data.get("login_type")

        if not login_username or not login_password:
            raise forms.ValidationError("All fields are required.")
        
        return cleaned_data
