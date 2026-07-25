from django.http import HttpResponse
from django.shortcuts import render , redirect
from django.views.generic import ListView , DetailView
from django.shortcuts import get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.mail import send_mail

# Create your views here.

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
        'forms': form,
    }
    return render(request, 'forms/comment.html', context)


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