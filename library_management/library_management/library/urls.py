from django.urls import path , reverse_lazy
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
    path('ticket' , views.ticket , name = 'ticket'),
    path('password_change/' , auth_views.PasswordChangeView.as_view(success_url = reverse_lazy('library:password_change_done')) , name = 'password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view() , name = 'password_change_done'),
    path('password_reset/' , auth_views.PasswordResetView.as_view(success_url = reverse_lazy('library:password_reset_done')) , name = 'password_reset'),
    path('password_reset/done/' , auth_views.PasswordResetDoneView.as_view() , name = 'password_reset_done'),
    path('password_reset/<uidb64>/<token>/' , auth_views.PasswordResetConfirmView.as_view(success_url = reverse_lazy('library:password_reset_complete')) , name = 'password_reset_confirm'),
    path('password_reset/complete' , auth_views.PasswordResetCompleteView.as_view() , name = 'password_reset_complete'),
]