from datetime import  timedelta
from django.urls import reverse
from django.db import models
from django_jalali.db import models as jmodels
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Category(models.Model):
    class Name(models.TextChoices):
        SCIENCE_FICTION = 'SF' , 'Science Fiction'
        NOVAL = 'Nl' , 'Novel'
        HORROR ='HR' , 'Horror'
        CRIM = 'CM' , 'Crim'
        EDUCATIONAL = 'EC' , 'Educational'
        BIOGRAPHY = 'BG' , 'Biography'
        HISTORY = 'HS' , 'History'
        ROMANCE = 'RO' , 'Romance'
        PSYCHOLOGY = 'PS' , 'Psychology'
        TECHNOLOGY = 'TE' , 'Technology'
        OTHERS = 'OT' , 'Others'

    name = models.CharField(choices=Name.choices, max_length=50 , default = Name.OTHERS)
    slug = models.SlugField(max_length=50)
    description = models.TextField()
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        LIBRARIAN = 'Li' , 'Librarian'
        MEMBER = 'Mr' , 'Member'

    phone = models.CharField(max_length = 11)
    employee_code = models.CharField(max_length = 50 , unique = True , blank = True , null = True)
    role = models.CharField(choices=Role.choices, default = Role.MEMBER , max_length=10)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Author(models.Model):
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 100)
    biography = models.TextField()
    birth_date = jmodels.jDateField()
    nationality = models.CharField(max_length = 50)

    class Meta:
        ordering = ['birth_date']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Publisher(models.Model):
    name = models.CharField(max_length = 100)
    address = models.TextField()
    phone = models.CharField(max_length = 11)
    email = models.CharField(max_length = 100)
    website_url = models.CharField(max_length = 100 , blank = True , null = True)
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length = 100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE , related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE , related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE , related_name='books')
    isbn = models.CharField(max_length = 100)
    description = models.TextField()
    publication_date = jmodels.jDateField()
    pages = models.IntegerField()
    total_copies = models.IntegerField()
    total_available_copies = models.IntegerField()
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields = ['title' , 'publisher']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'id':self.id})


class Request(models.Model):
    class RequestType(models.TextChoices):
        RETURN = 'Rt' , 'Return'
        BORROW = 'Bro' , 'Borrow'

    class Status(models.TextChoices):
        PENDING = 'PE' , 'Pending'
        APPROVED = 'AP' , 'Approved'
        REJECTED = 'RE' , 'Rejected'

    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='user_requests')
    book = models.ForeignKey(Book, on_delete=models.CASCADE , related_name='requests')
    request_date = jmodels.jDateField()
    request_type = models.CharField(choices=RequestType.choices, default = RequestType.BORROW , max_length=50 )
    status = models.CharField(choices=Status.choices, default = Status.PENDING , max_length=50 )
    librarian = models.ForeignKey(User, on_delete=models.CASCADE , related_name='librarian_requests' , null = True , blank = True)

    class Meta:
        ordering = ['-request_date']

        indexes = [
            models.Index(fields = ['request_date' , 'status']),
        ]

    def __str__(self):
        return f'{self.user} -> {self.book}'


class Loan(models.Model):
    class StatusChoices(models.TextChoices):
        BORROWED = 'Br' , 'Borrowed'
        RETURNED = 'RT' , 'Returned'
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE , related_name='loans')
    borrow_date = jmodels.jDateField()
    due_date = jmodels.jDateField()
    return_date = jmodels.jDateField(null=True , blank=True)
    borrow_librarian = models.ForeignKey(User, on_delete=models.SET_NULL , null=True , related_name='borrows')
    return_librarian = models.ForeignKey(User, on_delete=models.CASCADE , related_name='returns' , default = None , null=True,
    blank=True)
    status = models.CharField(choices=StatusChoices.choices, default = StatusChoices.BORROWED , max_length=50)

    def __str__(self):
        return f'{self.user} -> {self.book}'

    def save(self , *args , **kwargs):
        if self.borrow_date:
            self.due_date = self.borrow_date + timedelta(days=30)
        super().save(*args , **kwargs)

def censor(text):
    bad_word = ['loser']
    for word in bad_word:
        text = text.replace(word, '*' * len(word))
    return text

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='comments')
    book = models.ForeignKey(Book, on_delete=models.CASCADE , related_name='comments')
    text = models.TextField()
    rating = models.PositiveSmallIntegerField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True , related_name = 'replies')
    is_approved = models.BooleanField(default=False)
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} -> {self.book}'

    def save(self , *args , **kwargs):
        self.text = censor(self.text)
        super().save(*args , **kwargs)




