from django.contrib import admin

from books.models import (Author, Book, Category, Publisher, BookInstance,
                          Operation, Loan, Comment, FavoriteBook, AuthorComment, )

# Register your models here.
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Publisher)
admin.site.register(Operation)
admin.site.register(BookInstance)
admin.site.register(Loan)
admin.site.register(Comment)
admin.site.register(FavoriteBook)
admin.site.register(AuthorComment)
