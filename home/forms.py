from django import forms

class ManagerSignupForm(forms.Form):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)
    username = forms.CharField(max_length=100)
    email = forms.EmailField(label="Email")
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

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

class PrivateSignupForm(forms.Form):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)
    username = forms.CharField(max_length=100)
    email = forms.EmailField(label="Email")
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

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


class LoginForm(forms.Form):
    login_username = forms.CharField(max_length=100)
    login_password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    login_type = forms.ChoiceField(choices=[('manager', 'Manager'), ('private', 'Private'), ('worker', 'Worker')])
