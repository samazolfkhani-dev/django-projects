from django.shortcuts import render
from django.views.generic import ListView , DetailView
from django.shortcuts import get_object_or_404
from .forms import *
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


def comment(request , book_id , user_id ):
    user = get_object_or_404(User , pk=user_id)
    book = get_object_or_404(Book , pk=book_id)
    form = CommentForm(request.post)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = user
        comment.book = book
        comment.save()
    context = {
        'user': user,
        'comment': comment,
        'form': form,
    }
    return render(request, 'forms/comment.html', context)