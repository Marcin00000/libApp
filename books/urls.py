from django.urls import path
from . import views
from .views import BookDetailView, BookListView, AuthorListView


urlpatterns = [
    # path('', views.home, name='home'),
    path('', BookListView.as_view(), name='home'),
    path('author/<slug>/', AuthorListView.as_view(), name='author-books'),

    # path('books/', views.BookListView.as_view(), name='books'),
    # path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    # path('authors/', views.AuthorListView.as_view(), name='authors'),
    # path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),

# path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('book/<slug>/', BookDetailView.as_view(), name='book-detail'),
]