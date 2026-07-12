from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    path('', views.index, name='index'),
    path('book_list/', views.BookListView.as_view(), name='book_list'),
    path('book_list/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
]