from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['user' , 'book' , 'text' , 'rating' , 'parent']

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100 , required=True)
    password = forms.CharField(widget=forms.PasswordInput , required=True , max_length=250)

class LibrarianRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput , required=True , max_length=20)
    password2 = forms.CharField(widget=forms.PasswordInput , required=True , max_length=20)
    class Meta:
        model = User
        fields = ['username' , 'first_name' , 'last_name' , 'email' , 'phone' , 'employee_code']
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match!")
        return cd['password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists!")
        return username

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone already exists!")
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists!")
        return email


class MemberRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True, max_length=20)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, max_length=20)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match!")
        return cd['password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists!")
        return username

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone already exists!")
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists!")
        return email