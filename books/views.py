from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin

from .forms import CommentForm

from books.forms import BorrowBookForm
from books.models import Book, Author, Category, BookInstance, Operation, Loan, Comment


def home(request):
    books = Book.objects.all()
    borrowed_count = Loan.objects.filter(returned=False).count()
    print(f"Borrowed count: {borrowed_count}")  # Debugging line
    context = {
        'books': books,
        'borrowed_count': borrowed_count
    }

    return render(request, 'books/home2.html', context)


class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 8
    ordering = ['title']


class AuthorListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 4
    ordering = ['title']

    def get_queryset(self):
        xx = get_object_or_404(Author, slug=self.kwargs.get('slug'))
        return Book.objects.filter(author=xx)


class CategoryListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 4
    ordering = ['title']

    def get_queryset(self):
        xx = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return Book.objects.filter(category=xx)


class BookDetailView(FormMixin, DetailView):
    model = Book
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_books_count'] = BookInstance.objects.filter(book=self.object, status='available').count()
        context['comments'] = Comment.objects.filter(book=self.object).order_by('-created_at')
        context['has_read'] = Loan.objects.filter(user=self.request.user, book_instance__book=self.object,
                                                  returned=True).exists() if self.request.user.is_authenticated else False  # Czy książka została przeczytana
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.book = self.get_object()
        form.instance.user = self.request.user
        form.instance.is_read = Loan.objects.filter(user=self.request.user, book_instance__book=self.object,
                                                    returned=True).exists()  # Ustawienie is_read
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


def borrow_book(request):
    if request.method == 'POST':
        form = BorrowBookForm(request.POST)
        if form.is_valid():
            # Sprawdzenie limitu wypożyczeń
            active_loans_count = Loan.objects.filter(user=request.user, returned=False).count()
            if active_loans_count >= Loan.MAX_LOANS:
                messages.error(request, "Osiągnąłeś maksymalny limit wypożyczeń. Zwolnij jedną z książek, aby wypożyczyć nową.")
                return redirect('borrow_book')

            # Przetwarzanie wypożyczenia książki
            id_code = form.cleaned_data['id_code']
            try:
                book_instance = BookInstance.objects.get(id_code=id_code)
            except BookInstance.DoesNotExist:
                messages.error(request, f'Nie znaleziono książki o kodzie {id_code}.')
                return redirect('borrow_book')

            # Sprawdzenie dostępności książki
            if book_instance.status != 'available':
                messages.error(request, f'Książka "{book_instance}" nie jest dostępna do wypożyczenia.')
                return redirect('borrow_book')

            # Tworzenie wypożyczenia
            due_date = timezone.now() + timezone.timedelta(days=14)
            Loan.objects.create(
                book_instance=book_instance,
                user=request.user,
                due_date=due_date
            )

            # Aktualizacja statusu książki
            book_instance.status = 'borrowed'
            book_instance.save()

            messages.success(request, f'Pomyślnie wypożyczyłeś książkę: {book_instance}.')
            return redirect('borrow_book')
    else:
        form = BorrowBookForm()

    return render(request, 'books/borrow_book.html', {'form': form})


@login_required
def return_book(request):
    if request.method == 'POST':
        form = BorrowBookForm(request.POST)  # Używamy tego samego formularza do wyszukiwania książki
        if form.is_valid():
            id_code = form.cleaned_data['id_code']

            # Sprawdzamy, czy istnieje egzemplarz książki o podanym kodzie
            try:
                book_instance = BookInstance.objects.get(id_code=id_code)
            except BookInstance.DoesNotExist:
                messages.error(request, f'Nie znaleziono książki o kodzie {id_code}.')
                return redirect('return_book')

            # Sprawdzamy, czy książka jest wypożyczona przez zalogowanego użytkownika
            try:
                loan = Loan.objects.get(book_instance=book_instance, user=request.user, returned=False)
            except Loan.DoesNotExist:
                messages.error(request, f'Książka "{book_instance}" nie jest aktualnie wypożyczona przez Ciebie.')
                return redirect('return_book')

            # # Ustawienie daty zwrotu i aktualizacja statusu wypożyczenia
            # loan.returned = True
            # loan.returned_date = timezone.now()
            # loan.save()
            #
            # # Zmiana statusu książki na 'available'
            # book_instance.status = 'available'
            # book_instance.save()

            # Dodanie operacji zwrotu do modelu Operation
            Operation.objects.create(
                book_instance=book_instance,
                user=request.user,
                operation_type='return',
                loan=loan
            )

            messages.success(request, f'Pomyślnie zwróciłeś książkę: {book_instance}.')
            return redirect('return_book')
    else:
        form = BorrowBookForm()

    return render(request, 'books/return_book.html', {'form': form})


@login_required
def borrowed_books_view(request):
    # Pobranie wszystkich aktywnych wypożyczeń dla zalogowanego użytkownika, które nie zostały zwrócone
    loans = Loan.objects.filter(user=request.user, returned=False)

    # Dodaj bieżący czas do kontekstu
    current_time = timezone.now()

    # Dodaj liczbę dni pozostałych do zwrotu do każdego wypożyczenia
    for loan in loans:
        loan.days_remaining = (loan.due_date - current_time.date()).days

    # Przekazanie bezpośrednio listy wypożyczeń do szablonu
    return render(request, 'books/borrowed_books.html', {'loans': loans, 'now': current_time})


def book_search(request):
    query = request.GET.get('q')  # Pobierz zapytanie z formularza
    books = Book.objects.none()  # Pusty QuerySet domyślnie

    if query:
        # Wyszukiwanie książek na podstawie tytułu, opisu lub autora
        books = Book.objects.filter(
            title__icontains=query
        ) | Book.objects.filter(
            description__icontains=query
        ) | Book.objects.filter(
            author__name__icontains=query  # Użyj 'name' jako pola modelu Author
        ) | Book.objects.filter(
            author__surname__icontains=query  # Użyj 'name' jako pola modelu Author
        )

    context = {
        'books': books,
        'query': query,
    }
    return render(request, 'books/book_list.html', context)  # Możesz zmienić szablon na odpowiedni


@login_required
def read_books_view(request):
    # Pobranie wszystkich wypożyczeń dla zalogowanego użytkownika, które zostały zwrócone
    loans = Loan.objects.filter(user=request.user, returned=True).order_by('-returned_date')

    return render(request, 'books/read_books.html', {'loans': loans})


