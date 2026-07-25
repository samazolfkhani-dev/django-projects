from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import *
app_name = "library"

urlpatterns = [
    path('', views.index, name='index'),
    path('book_list/', views.BookListView.as_view(), name='book_list'),
    path('book_list/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book_list/<int:book_id><int:user_id>/comments' , views.comment , name='book_comment'),
    path('login/' , auth_views.LoginView.as_view(template_name="registration/login.html" , authentication_form = LoginForm) , name='login'),
    path('logout/' , auth_views.LogoutView.as_view() , name='logout'),
    path('profile/' , views.profile , name='profile'),
    path('profile/member/' , views.member_profile , name='member_profile'),
    path('profile/librarian/' , views.librarian_profile , name='librarian_profile'),
    path('uregister/' , views.librarian_register , name = 'user_register'),
    path('mregister/' , views.member_register , name = 'member_register'),
    path('user_detail/' , views.user_detail , name = 'user_detail'),
    path('ticket' , views.ticket , name = 'ticket')
]