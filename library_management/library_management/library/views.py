from django.http import HttpResponse , JsonResponse
from django.shortcuts import render , redirect
from django.views.generic import ListView , DetailView
from django.shortcuts import get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.core.paginator import Paginator , EmptyPage , PageNotAnInteger
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.postgres.search import SearchVector , SearchQuery , SearchRank , TrigramSimilarity
from django.views.decorators.http import require_POST
import jdatetime
from django.db.models import Prefetch
from django.contrib import messages
# Create your views here.

def index(request):
    return render(request, 'library/home.html')

def book_list(request , tag_slug = None):
    books = Book.objects.select_related('author' , 'publisher' , 'category').prefetch_related('tags' , Prefetch('images' , to_attr = 'prefetched_images'))
    tag = None
    if tag_slug :
        tag = get_object_or_404(Tag , slug = tag_slug)
        books = books.filter(tags__in = [tag])
    page = request.GET.get('page')
    paginator = Paginator(books , 3)
    try :
        books = paginator.page(page)
    except PageNotAnInteger :
        books = paginator.page(1)
    except EmptyPage :
        books = paginator.page(1)
    context = {
        'books' : books ,
        'tag' : tag ,
    }
    return render(request , 'library/book_list.html' , context)


def book_detail(request, id):
    book = get_object_or_404(Book.objects.select_related('author' , 'publisher' , 'category').prefetch_related('tags' , 'images') , id=id)
    book_tags_ids = book.tags.values_list("id", flat=True)
    similar_books = (
        Book.objects.select_related('author').prefetch_related('tags').filter(tags__in=book_tags_ids)
        .exclude(id=book.id)
        .annotate(same_tags=Count("tags"))
        .order_by("-same_tags", "-created_at")[:2])
    comments = book.comments.select_related('user')  
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
            messages.success(request , "Your Comment Has Been Submitted!")
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
    member = get_object_or_404(User, pk=request.user.id)
    loans = Loan.objects.filter(user=request.user , status = Loan.StatusChoices.BORROWED).\
        select_related('book' , 'borrow_librarian' , 'return_librarian')
    requests = Request.objects.filter(user = member , status = Request.Status.PENDING).\
        select_related('book')
    comments = Comment.objects.filter(user=request.user).select_related('book')
    context = {
        'member': member,
        'loans': loans,
        'comments': comments,
        'requests' : requests
    }
    return render(request , 'library/member_profile.html' , context)



@login_required
def librarian_profile(request):
    librarian = get_object_or_404(User , pk=request.user.id)
    borrow_loans = Loan.objects.filter(borrow_librarian=request.user).\
        select_related('book' , 'user')
    return_loans = Loan.objects.filter(return_librarian=request.user).\
        select_related('book' , 'user')
    loans = borrow_loans.union(return_loans)
    comments = Comment.objects.filter(user=request.user).select_related('book')
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
            messages.success(request , "Your Information Has Been Successfully Submitted!")
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
            messages.success(request , "Your Information Has Been Successfully Submitted!")
            return render(request , 'registration/register_done.html' , {'user':user })
    else :
        form = MemberRegisterForm()
    return render(request, 'forms/register.html' , {'form':form})

def user_detail(request):
    user = get_object_or_404(User , pk=request.user.id)
    loans = Loan.objects.filter(user=request.user).select_related('book' , 'borrow_librarian' , 'return_librarian')
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
            messages.success(request , "Your Ticket Has Been Successfully Sent To Supports!")
    else:
        form = TicketForm()
    return render(request,'forms/ticket.html',{'form': form,'sent': sent})


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
            messages.success(request , "The Book Has Been Successfully Added!")
            return redirect('library:index')
    else:
        form = CreateBookForm()
    return render(request,'forms/add_book.html',{'form': form})


def author_list(request):
    authors = Author.objects.all()
    page = request.GET.get('page')
    paginator = Paginator(authors , 3)
    try :
        authors = paginator.page(page)
    except PageNotAnInteger :
        authors = paginator.page(1)
    except EmptyPage :
        authors = []
    if request.GET.get('ajax'):
        return render(request , 'library/author_list_ajax.html' , {'authors' : authors})
    return render(request , 'library/author_list.html' , {'authors' : authors})

def author_detail(request , id):
    author = get_object_or_404(Author , id = id)
    books = Book.objects.filter(author = author).select_related('publisher' , 'category')
    return render(request , 'library/author_detail.html' , {'author' : author , 'books' : books})


def publisher_list(request):
    publishers = Publisher.objects.all()
    paginator = Paginator(publishers , 3)
    page_number = request.GET.get('page' , 1)
    publishers = paginator.page(page_number)
    return render(request , 'library/publisher_list.html' , {'publishers' : publishers})

def publisher_detail(request , id):
    publisher = get_object_or_404(Publisher , id = id)
    books = Book.objects.filter(publisher = publisher).select_related('category' , 'author')
    return render(request , 'library/publisher_detail.html' , {'publisher' : publisher , 'books' : books})

@login_required
def delete_book(request , id):
    book = get_object_or_404(Book , id = id)
    if request.method == "POST" :
        book.delete()
        messages.success(request , "The Book Has Been Successfully Deleted!")
        return redirect('library:book_list')
    return render(request ,'forms/delete_book.html' , {'book' : book})

@login_required
def edit_book(request , id):
    if request.user.role != User.Role.LIBRARIAN:
        raise PermissionDenied
    else :
        book = get_object_or_404(Book , id = id)
        if request.method == "POST" :
            form = CreateBookForm(request.POST , request.FILES , instance = book)
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
                messages.success(request , "The Book Has Been Successfully Edited!")
                return redirect('library:index')
        else:
            form = CreateBookForm(instance = book)
            return render(request,'forms/add_book.html',{'form': form})


def search(request):
    query = None
    authors = []
    publishers = []
    books = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_query = SearchQuery(query)
            # author_search
            author_vector = (SearchVector('first_name', weight='A') +SearchVector('last_name', weight='A') +\
                             SearchVector('biography', weight='B') + SearchVector('nationality', weight='C'))
            authors = Author.objects.annotate(rank=SearchRank(author_vector,search_query),similarity=(TrigramSimilarity('first_name', query) +\
                        TrigramSimilarity('last_name', query))).filter(Q(rank__gte=0.3) | Q(similarity__gte=0.5)).order_by('-rank','-similarity')
            # publisher_search
            publisher_vector = (SearchVector('name', weight='A') + SearchVector('address', weight='B') + SearchVector('email', weight='C'))
            publishers = Publisher.objects.annotate(rank=SearchRank(publisher_vector,search_query),\
                                                     similarity=TrigramSimilarity('name',query)).\
                                                        filter(Q(rank__gte=0.3) |Q(similarity__gte=0.5)).\
                                                            order_by('-rank','-similarity')
            # book_search
            book_vector = (
                SearchVector( 'title', weight='A') +SearchVector('author__first_name',weight='A') +\
                SearchVector('author__last_name',weight='A') + SearchVector('publisher__name',weight='B') +\
                SearchVector('isbn',weight='B') + SearchVector('description',weight='C')
            )

            books = (
                Book.objects

                .annotate(
                    rank=SearchRank(
                        book_vector,
                        search_query
                    ),

                    similarity=(
                        TrigramSimilarity(
                            'title',
                            query
                        )

                        +

                        TrigramSimilarity(
                            'author__first_name',
                            query
                        )

                        +

                        TrigramSimilarity(
                            'author__last_name',
                            query
                        )

                        +

                        TrigramSimilarity(
                            'publisher__name',
                            query
                        )
                    )
                )

                .filter(
                    Q(rank__gte=0.3) |
                    Q(similarity__gte=0.5)
                )

                .select_related(
                    'author'
                )

                .order_by(
                    '-rank',
                    '-similarity'
                )
            )

    context = {
        'query': query,
        'authors': authors,
        'publishers': publishers,
        'books': books,
    }

    return render(
        request,
        'library/search.html',
        context
    )

@login_required
@require_POST
def book_like(request):
    book_id = request.POST.get('book_id')
    if book_id is not None :
        book = get_object_or_404(Book , id = book_id)
        user = request.user

        if user in book.likes.all():
            book.likes.remove(user)
            liked = False
        else :
            book.likes.add(user)
            liked = True
        book_likes_count = book.likes.count()
        response_data ={
            'liked' : liked ,
            'likes_count' : book_likes_count
        }
    else :
        response_data = {'error' : 'Invalid Book Id!'}

    return JsonResponse(response_data)


@login_required
@require_POST
def author_like(request):
    author_id = request.POST.get('author_id')
    if author_id is not None :
        author = get_object_or_404(Author , id = author_id)
        user = request.user

        if user in author.likes.all():
            author.likes.remove(user)
            liked = False
        else :
            author.likes.add(user)
            liked = True
        author_likes_count = author.likes.count()
        response_data ={
            'liked' : liked ,
            'likes_count' : author_likes_count
        }
    else :
        response_data = {'error' : 'Invalid Author Id!'}

    return JsonResponse(response_data)


@login_required
@require_POST
def publisher_like(request):
    publisher_id = request.POST.get('publisher_id')
    if publisher_id is not None :
        publisher = get_object_or_404(Publisher , id = publisher_id)
        user = request.user

        if user in publisher.likes.all():
            publisher.likes.remove(user)
            liked = False
        else :
            publisher.likes.add(user)
            liked = True
        publisher_likes_count = publisher.likes.count()
        response_data ={
            'liked' : liked ,
            'likes_count' : publisher_likes_count
        }
    else :
        response_data = {'error' : 'Invalid Publisher Id!'}

    return JsonResponse(response_data)

@login_required
@require_POST
def book_request(request):
    book_id = request.POST.get('book_id')
    book = get_object_or_404(Book , id = book_id)
    already_borrowed = Loan.objects.filter(user = request.user , book = book , status = Loan.StatusChoices.BORROWED).exists()
    already_request = Request.objects.filter(user = request.user , book = book , request_type = Request.RequestType.BORROW , status = Request.Status.PENDING).exists()
    if already_borrowed :
        return JsonResponse({
            'success' : False ,
            'message' : 'You Already Have This Book!' ,
            'message_type' : 'warning'
        })
    if already_request :
        return JsonResponse({
            'success' : False ,
            'message' : 'You Already Have A Pending Request!' ,
            'message_type' : 'warning'
        })
    if not request.user.is_active :
        return JsonResponse({
            'success' : False ,
            'message' : 'You Are Disabled By Admin Of Site!',
            'message_type' : 'error'
        })
    Request.objects.create(user = request.user , book = book , request_type = Request.RequestType.BORROW)
    return JsonResponse({
        'success' : True ,
        'message' : 'The Request Has Been Successfully Added!',
        'message_type' : 'success'
    })

@login_required
def request_list(request):
    if request.user.role == User.Role.LIBRARIAN:
        borrow_requests = Request.objects.filter(request_type = Request.RequestType.BORROW , status = Request.Status.PENDING).\
            select_related('book' , 'user')
        return_requests = Request.objects.filter(request_type = Request.RequestType.RETURN , status = Request.Status.PENDING).\
            select_related('book' , 'user')
        context ={
            'borrow_request' : borrow_requests ,
            'return_request' : return_requests
        }
        return render(request , 'library/request.html' , context = context)
    else :
        raise PermissionDenied("Access Denied!")

@require_POST
@login_required
def borrow_book(request) :
    if request.user.role == User.Role.LIBRARIAN :
        librarian = request.user
        request_id = request.POST.get('request_id')

        if request_id is None:
            return JsonResponse({'success' : False , 'message' : 'No Such Request!' , 'message_type' : 'error'})
        
        r = get_object_or_404(Request , id = request_id , status = Request.Status.PENDING ,\
                             request_type=Request.RequestType.BORROW)
        book = r.book

        if book.total_available_copies <= 0 :
                return JsonResponse({'success' : False , 'message' : 'This Book Is Not Available!' , 'message_type' : 'warning'})
        
        loan = Loan.objects.create(user = r.user , book = r.book , borrow_librarian = librarian , status = Loan.StatusChoices.BORROWED ,\
                                    due_date = jdatetime.date.today() + timedelta(days = 30) ,\
                                    borrow_date = jdatetime.date.today())
        
        book.total_available_copies -= 1
        book.save(update_fields=['total_available_copies'])

        r.status = Request.Status.APPROVED
        r.librarian = librarian
        r.save(update_fields=['status' , 'librarian'])
        return JsonResponse({'success' : True , 'message' : 'The Request Has Been Successfully Submitted!' , 'message_type' : 'success'})
    
    else :
        raise PermissionDenied('Access Denied!')

@require_POST
@login_required
def reject_borrow(request):
    if request.user.role == User.Role.LIBRARIAN :
        librarian = request.user
        request_id = request.POST.get('request_id')
        if request_id is None:
            return JsonResponse({'success' : False , 'message' : 'No Such Request!' , 'message_type' : 'error'})
        r = get_object_or_404(Request , id = request_id , status = Request.Status.PENDING , request_type=Request.RequestType.BORROW)
        r.status = Request.Status.REJECTED
        r.librarian = librarian
        r.save(update_fields=['status' , 'librarian'])
        return JsonResponse({'success' : True ,  'message' : 'The Request Has Been Successfully Rejected!' , 'message_type' : 'success'})
    else :
        raise PermissionDenied('Access Denied!')

@login_required
@require_POST
def return_request(request):
    loan_id = request.POST.get('loan_id')
    if loan_id :
        loan = get_object_or_404(Loan , id = loan_id , user = request.user , status = Loan.StatusChoices.BORROWED)
        already_request = Request.objects.filter(user = loan.user , book = loan.book , request_type = Request.RequestType.RETURN , status = Request.Status.PENDING).exists()
        if already_request :
            return JsonResponse({
                'success' : False ,
                'message' : 'You Already Have A Pending Request!' ,
                'message_type' : 'warning'
            })
        Request.objects.create(user = loan.user , book = loan.book , request_type = Request.RequestType.RETURN)
        return JsonResponse({
            'success' : True ,
            'message' : 'The Request Has Been Successfully Sent!' ,
            'message_type' : 'success'
        })
    return JsonResponse({
        'success' : False ,
        'Message' : 'Undefiend Loan!' ,
        'message_type' : 'erro'
    })
        

@login_required
@require_POST
def return_request_accepting(request):
    if request.user.role == User.Role.LIBRARIAN :
        librarian = request.user
        request_id = request.POST.get('request_id')
        if request_id is None:
            return JsonResponse({'success' : False , 'message' : 'No Such Request!' , 'message_type' : 'error'})
        r = get_object_or_404(Request , id = request_id , status = Request.Status.PENDING , request_type=Request.RequestType.RETURN)
        book = r.book
        loan = get_object_or_404(Loan , user = r.user , book = r.book , status = Loan.StatusChoices.BORROWED)
        loan.status = Loan.StatusChoices.RETURNED
        loan.return_date = jdatetime.date.today()
        loan.return_librarian = librarian
        loan.save(update_fields=['status' , 'return_date' , 'return_librarian'])
        book.total_available_copies += 1
        book.save(update_fields=['total_available_copies'])
        r.status = Request.Status.APPROVED
        r.librarian = librarian
        r.save(update_fields=['status' , 'librarian'])
        return JsonResponse({'success' : True , 'message' : 'The Book Has Been Successfully Returned!' , 'message_type' : 'success'})
    else :
        raise PermissionDenied('Access Denied!')


    