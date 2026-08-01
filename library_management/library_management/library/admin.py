from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description' , 'created_at', 'updated_at']
    ordering = ['id', 'name']
    list_filter = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    date_hierarchy = 'created_at'
    prepopulated_fields = {'slug': ['name']}
    list_display_links = ['name', 'description' , 'created_at', 'updated_at']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'role' , 'is_active']
    ordering = ['id']
    list_filter = ['is_active' , 'role']
    search_fields = ['employee_code', 'first_name', 'last_name']
    list_display_links = ['first_name', 'last_name', 'phone' , 'is_active' , 'role']
    def get_fieldsets(self , request , obj=None):
        # we override this to separate the screen shown of librarian and member in admin panel
        fieldsets = super().get_fieldsets(request , obj)
        if obj :
            if obj.role == User.Role.LIBRARIAN :
                fieldsets += (
                    ("Additional Information", {"fields" : ("employee_code" , "phone" , "role" ,)}) ,
                )
            else :
                fieldsets += (
                    ("Additional Information" , {"fields" : ("phone" , "role" , )}) ,
                )
        return fieldsets

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'birth_date', 'nationality']
    ordering = ['id', 'first_name' , 'last_name']
    list_filter = ['first_name', 'last_name' , 'nationality']
    search_fields = ['first_name' , 'last_name' ]
    list_display_links = ['first_name', 'last_name', 'birth_date', 'nationality']

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'website_url']
    ordering = ['id', 'name']
    list_filter = ['name']
    search_fields = ['name']
    list_display_links = ['name', 'phone', 'email', 'website_url']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title' , 'author' , 'publisher', 'isbn' , 'publication_date' , 'pages' , 'total_copies' , 'total_available_copies' , 'tag_list']
    ordering = ['id', 'title' , 'publication_date']
    list_filter = ['title', 'author', 'publisher' , 'publication_date']
    search_fields = ['title', 'author', 'publisher']
    date_hierarchy = 'publication_date'
    list_display_links = ['title' , 'author' , 'publisher', 'isbn' , 'publication_date' , 'pages' , 'total_copies' , 'total_available_copies']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self , obj):
        return ' , '.join(o.name for o in obj.tags.all())


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'request_date', 'request_type' , 'status']
    ordering = ['id', 'request_date']
    list_filter = ['request_date']
    date_hierarchy = 'request_date'
    list_display_links = ['user', 'book', 'request_date', 'request_type' , 'status' , 'status']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrow_date', 'return_date' , 'status']
    ordering = ['id', 'return_date']
    list_filter = ['return_date', 'status']
    date_hierarchy = 'due_date'
    list_display_links = ['user', 'book', 'borrow_date', 'return_date' , 'status']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['book', 'user']
    ordering = ['id', 'created']
    list_display_links = ['book', 'user']