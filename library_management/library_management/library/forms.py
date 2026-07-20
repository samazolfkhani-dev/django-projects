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