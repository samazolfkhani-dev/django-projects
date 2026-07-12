from django.shortcuts import render
from django.views.generic import ListView , DetailView
# Create your views here.
from .models import *

def index(request):
    return render(request, 'library/home.html')

class BookListView(ListView):
    queryset = Book.objects.all()
    template_name = 'library/book_list.html'
    paginate_by = 4
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail.html'