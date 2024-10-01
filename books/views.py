from django.shortcuts import render
from django.views.generic import DetailView
from books.models import Book


# Create your views here.

def home(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'books/home.html', context)


def BookDetailView(DetailView):
    model = Book