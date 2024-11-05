from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin
from django.shortcuts import render, get_object_or_404
from books.forms import BorrowBookForm
from books.models import Book, Author, Category, BookInstance, Operation, Loan, Comment, FavoriteBook
from .forms import CommentForm


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


# class BookDetailView(FormMixin, DetailView):
#     model = Book
#     form_class = CommentForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['available_books_count'] = BookInstance.objects.filter(book=self.object, status='available').count()
#         context['comments'] = Comment.objects.filter(book=self.object).order_by('-created_at')
#         context['has_read'] = Loan.objects.filter(user=self.request.user, book_instance__book=self.object,
#                                                   returned=True).exists() if self.request.user.is_authenticated else False
#         context['is_favorite'] = FavoriteBook.objects.filter(user=self.request.user, book=self.object).exists() if self.request.user.is_authenticated else False
#         return context
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     def form_valid(self, form):
#         form.instance.book = self.get_object()
#         form.instance.user = self.request.user
#         form.instance.is_read = Loan.objects.filter(user=self.request.user, book_instance__book=self.object,
#                                                     returned=True).exists()
#         form.save()
#         messages.success(self.request, "Twój komentarz został dodany.")
#         return super().form_valid(form)
#
#     def add_to_favorites(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             book = self.get_object()
#             favorite, created = FavoriteBook.objects.get_or_create(user=request.user, book=book)
#             if not created:
#                 favorite.delete()  # Usuń z ulubionych
#             return JsonResponse({'success': True, 'is_favorite': not created})
#
#     def get_success_url(self):
#         return self.request.path

class BookDetailView(FormMixin, DetailView):
    model = Book
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_books_count'] = BookInstance.objects.filter(book=self.object, status='available').count()
        context['comments'] = Comment.objects.filter(book=self.object).order_by('-created_at')
        context['has_read'] = Loan.objects.filter(
            user=self.request.user, book_instance__book=self.object, returned=True
        ).exists() if self.request.user.is_authenticated else False
        context['is_favorite'] = FavoriteBook.objects.filter(
            user=self.request.user, book=self.object
        ).exists() if self.request.user.is_authenticated else False
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Obsługa ulubionych (AJAX)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.user.is_authenticated:
            favorite, created = FavoriteBook.objects.get_or_create(user=request.user, book=self.object)
            if not created:
                # messages.success(request, "Książka została dodana do ulubionych.")
            # else:
                favorite.delete()
                # messages.success(request, "Książka została usunięta z ulubionych.")
            return JsonResponse({'is_favorite': created})

        # Obsługa formularza dodawania komentarza
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.book = self.get_object()
        form.instance.user = self.request.user
        form.instance.is_read = Loan.objects.filter(
            user=self.request.user, book_instance__book=self.object, returned=True
        ).exists()
        form.save()
        messages.success(self.request, "Twój komentarz został dodany.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path



def borrow_book(request):
    if request.method == 'POST':
        form = BorrowBookForm(request.POST)
        if form.is_valid():
            # Sprawdzenie punktów karnych użytkownika
            profile = request.user.profile
            if profile.penalty_points > 30:
                messages.error(request, "Masz ponad 30 punktów karnych. Skontaktuj się z bibliotekarzem, aby uregulować stan punktów.")
                return redirect('borrow_book')

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
        form = BorrowBookForm(request.POST)
        if form.is_valid():
            id_code = form.cleaned_data['id_code']

            try:
                book_instance = BookInstance.objects.get(id_code=id_code)
            except BookInstance.DoesNotExist:
                messages.error(request, f'Nie znaleziono książki o kodzie {id_code}.')
                return redirect('return_book')

            try:
                loan = Loan.objects.get(book_instance=book_instance, user=request.user, returned=False)
            except Loan.DoesNotExist:
                messages.error(request, f'Książka "{book_instance}" nie jest aktualnie wypożyczona przez Ciebie.')
                return redirect('return_book')

            # Obliczanie liczby dni spóźnienia
            current_date = timezone.now().date()
            delay_days = (current_date - loan.due_date).days

            # Jeśli zwrot jest opóźniony, dodaj punkty karne
            if delay_days > 0:
                request.user.profile.penalty_points += delay_days
                request.user.profile.save()
                messages.warning(request, f'Dodano punkty karne za spóźnienie: {delay_days}')

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


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    book_slug = comment.book.slug  # Zapamiętujemy slug książki, aby przekierować użytkownika
    comment.delete()
    messages.success(request, "Twój komentarz został pomyślnie usunięty.")
    return redirect('book-detail', slug=book_slug)



class UserCommentsView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'books/user_comments.html'  # Szablon wyświetlający komentarze użytkownika
    context_object_name = 'comments'
    paginate_by = 10  # Opcjonalne: paginacja

    def get_queryset(self):
        # Zwraca tylko komentarze zalogowanego użytkownika
        return Comment.objects.filter(user=self.request.user).order_by('-created_at')


def about(request):
    return render(request, 'books/about.html')


def features_view(request):
    return render(request, 'books/features.html')


def faqs(request):
    return render(request, 'books/faqs.html')



def toggle_favorite(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    favorite, created = FavoriteBook.objects.get_or_create(user=request.user, book=book)

    if created:
        # Książka została dodana do ulubionych
        messages.success(request, f'Dodano książkę "{book.title}" do ulubionych.')
    else:
        # Książka została usunięta z ulubionych
        favorite.delete()
        messages.success(request, f'Usunięto książkę "{book.title}" z ulubionych.')

    return redirect('book-detail', slug=book.slug)



class FavoriteBooksView(ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'books/favorite_books.html'
    paginate_by = 8
    ordering = ['title']

    def get_queryset(self):
        # Pobierz ulubione książki dla aktualnie zalogowanego użytkownika
        return Book.objects.filter(favoritebook__user=self.request.user)