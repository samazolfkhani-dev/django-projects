from django.http import HttpResponse
from django.shortcuts import render , redirect
from django.views.generic import ListView , DetailView
from django.shortcuts import get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
# Create your views here.

def index(request):
    return render(request, 'library/home.html')

def book_list(request , tag_slug = None):
    books = Book.objects.all()
    tag = None
    if tag_slug :
        tag = get_object_or_404(Tag , slug = tag_slug)
        books = Book.objects.filter(tags__in = [tag])
    context = {
        'books' : books ,
        'tag' : tag ,
    }
    return render(request , 'library/book_list.html' , context)


def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    book_tags_ids = book.tags.values_list("id", flat=True)
    similar_books = (
        Book.objects.filter(tags__in=book_tags_ids)
        .exclude(id=book.id)
        .annotate(same_tags=Count("tags"))
        .order_by("-same_tags", "-created_at")[:2])
    comments = book.comments.all()   
    paginator = Paginator(comments ,4)    
    page_number = request.GET.get("page")
    comments = paginator.get_page(page_number)
    form = CommentForm()
    context = {
        "book": book,
        "comments": comments,
        "form": form,
        "similar_books": similar_books,
    }

    return render(request, "library/book_detail.html", context )

@login_required
def book_comment(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = book
            comment.user = request.user
            comment.save()
    return redirect("library:book_detail", id=book.id)


@login_required
def profile(request):
    if request.user.is_superuser:
        return redirect('/admin/')
    elif request.user.role == User.Role.LIBRARIAN:
        return redirect(reverse('library:librarian_profile'))
    else :
        return redirect(reverse('library:member_profile'))

@login_required
def member_profile(request):
    member = get_object_or_404(User , pk=request.user.id)
    loans = Loan.objects.filter(user=request.user)
    comments = Comment.objects.filter(user=request.user)
    context = {
        'member': member,
        'loans': loans,
        'comments': comments,
    }
    return render(request , 'library/member_profile.html' , context)



@login_required
def librarian_profile(request):
    librarian = get_object_or_404(User , pk=request.user.id)
    borrow_loans = Loan.objects.filter(borrow_librarian=request.user)
    return_loans = Loan.objects.filter(return_librarian=request.user)
    loans = borrow_loans or return_loans
    comments = Comment.objects.filter(user=request.user)
    context = {
        'librarian': librarian,
        'loans': loans,
        'comments': comments,
    }
    return render(request , 'library/librarian_profile.html' , context)

def librarian_register(request):
    if request.method == 'POST':
        form = LibrarianRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request , 'registration/register_done.html' , {'user':user })
    else :
        form = LibrarianRegisterForm()
    return render(request, 'forms/register.html' , {'form':form})

def member_register(request):
    if request.method == 'POST':
        form = MemberRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request , 'registration/register_done.html' , {'user':user })
    else :
        form = LibrarianRegisterForm()
    return render(request, 'forms/register.html' , {'form':form})

def user_detail(request):
    user = get_object_or_404(User , pk=request.user.id)
    loans = Loan.objects.filter(user=request.user)
    context = {
        'user': user,
        'loans': loans,
    }
    return render(request , 'library/user_detail.html' , context)

def ticket(request):
    sent = False
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            message = f"{cd['name']}\n{cd['email']}\n\n{cd['message']}"
            send_mail(cd['subject'],message,'samazolfkhani12@gmail.com',['samazolfkhani12@gmail.com'] , fail_silently=False)
            sent = True
    else:
        form = TicketForm()
    return render(
        request,'forms/ticket.html',{'form': form,'sent': sent}
    )


@login_required
def add_book(request):
    if request.user.role != User.Role.LIBRARIAN:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = CreateBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            images = [
                form.cleaned_data.get('image1'),
                form.cleaned_data.get('image2'),
                form.cleaned_data.get('image3'),
                form.cleaned_data.get('image4'),
            ]
            for image in images:
                if image:
                    Image.objects.create(
                        image_file=image,
                        book=book
                    )
            return redirect('library:index')
    else:
        form = CreateBookForm()
    return render(request,'forms/add_book.html',{'form': form})


def author_list(request):
    authors = Author.objects.all()
    paginator = Paginator(authors , 3)
    page_number = request.GET.get('page' , 1)
    authors = paginator.page(page_number)
    return render(request , 'library/author_list.html' , {'authors' : authors})

def author_detail(request , id):
    author = get_object_or_404(Author , id = id)
    return render(request , 'library/author_detail.html' , {'author' : author})


def publisher_list(request):
    publishers = Publisher.objects.all()
    paginator = Paginator(publishers , 3)
    page_number = request.GET.get('page' , 1)
    publishers = paginator.page(page_number)
    return render(request , 'library/publisher_list.html' , {'publishers' : publishers})

def publisher_detail(request , id):
    publisher = get_object_or_404(Publisher , id = id)
    return render(request , 'library/publisher_detail.html' , {'publisher' : publisher})

@login_required
def delete_book(request , id):
    book = get_object_or_404(Book , id = id)
    if request.method == "POST" :
        book.delete()
        return redirect('library:book_list')
    return render(request ,'forms/delete_book.html' , {'book' : book})

