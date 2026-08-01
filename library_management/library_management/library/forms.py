from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm

class CommentForm(forms.ModelForm):
    def clean_body(self):
        body = self.cleaned_data['body']
        if body :
            if not len(body) > 2 :
                raise forms.ValidationError("Comment must have at least 2 letters!")
            return body
    class Meta :
        model = Comment
        fields = ['body']
        widgets = {
            'body' : forms.Textarea(attrs={'placeholder' : 'Enter Your Comment :' , 'class' : 'comment_body'})
        }

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


class TicketForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea , required=True)
    name = forms.CharField(max_length=100 , required=True)
    email = forms.EmailField()
    phone = forms.CharField(max_length=11 , required=True)
    subject = forms.CharField()

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("Phone number must have digits!")
        return phone


class CreateBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title' , 'author' , 'publisher' , 'category' , 'isbn' , 'description' , 'publication_date' , 'pages' , 'total_copies' , 'total_available_copies' , 'tags']