from django.urls import path , reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import *
app_name = "library"

urlpatterns = [
    path('', views.index, name='index'),
    path('book_list/', views.book_list, name='book_list'),
    path('book_list/book/<slug:tag_slug>/', views.book_list, name='book_list_by_tag'),
    path('book_list/<int:id>/', views.book_detail , name='book_detail'),
    path('posts/<int:id>/comments' , views.book_comment, name = 'book_comment' ),
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
    path('add_book' , views.add_book , name = 'add_book'),
    path('author_list/<int:id>' , views.author_detail , name = "author_detail"),
    path('author_list' , views.author_list , name = "author_list"),
    path('publisher_list' , views.publisher_list , name = "publisher_list") , 
    path('publisher_list/<int:id>' , views.publisher_detail , name = "publisher_detail"),
    path('delete_book/<int:id>' , views.delete_book , name = "delete_book"),
    path('edit_book/<int:id>' , views.edit_book , name = "edit_book") ,
    path('search_book/' , views.search , name = "search"),
    path('book_likes/' , views.book_like , name = "book_like") ,
    path('author_likes/' , views.author_like , name = "author_like") ,
    path('publisher_likes/' , views.publisher_like , name = "publisher_like") ,
    path('book_request/' , views.book_request , name = "book_request") ,
    path('request_list/' , views.request_list , name = "request_list") ,
    path('borrow_book/' , views.borrow_book , name = "borrow_book") ,
    path('reject_borrow/' , views.reject_borrow , name = 'reject_borrow'),
]