from django.urls import path
from . import views
from .views import (BookDetailView, BookListView, AuthorListView, CategoryListView,
                    borrow_book, borrowed_books_view, return_book, book_search)

urlpatterns = [
    path('dom/', views.home, name='dom'),
    path('', BookListView.as_view(), name='home'),
    path('author/<slug>/', AuthorListView.as_view(), name='author-books'),
    path('category/<slug>/', CategoryListView.as_view(), name='category-books'),
    path('borrow/', borrow_book, name='borrow_book'),
    path('borrowed-book/', borrowed_books_view, name='borrowed_book'),
    path('return-book/', return_book , name='return_book'),
    path('search/', book_search, name='book_search'),


    # path('books/', views.BookListView.as_view(), name='books'),
    # path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    # path('authors/', views.AuthorListView.as_view(), name='authors'),
    # path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),

# path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('book/<slug>/', BookDetailView.as_view(), name='book-detail'),
]