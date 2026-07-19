from django import forms
from .models import *

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['user' , 'book' , 'text' , 'rating' , 'parent']