from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from books.models import Book, Author


# Create your views here.

def home(request):
    context = {'books': Book.objects.all()}
    return render(request, 'books/home.html', context)

class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 3

class AuthorListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 3

    # def get_queryset(self):
    #     return Book.objects.filter(author=self.kwargs['pk'])

    def get_queryset(self):
        xx = get_object_or_404(Author, slug=self.kwargs.get('slug'))
        return Book.objects.filter(author=xx)

class BookDetailView(DetailView):
    model = Book