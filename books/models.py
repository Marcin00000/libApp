import random
import string

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Imię")
    surname = models.CharField(max_length=100, verbose_name="Nazwisko")
    slug = AutoSlugField(populate_from='surname', null=True)

    def __str__(self):
        return self.name + " " + self.surname

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autorzy"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoria")
    slug = AutoSlugField(populate_from='name', null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"


class Publisher(models.Model):
    name = models.CharField(max_length=100, verbose_name="Wydawca")
    slug = AutoSlugField(populate_from='name', null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Wydawca"
        verbose_name_plural = "Wydawcy"


class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name="Tytuł")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="Autor")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoria")
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, verbose_name="Wydawca")
    ASIN = models.CharField(max_length=11, verbose_name="ASIN")
    publication_date = models.DateField(verbose_name="Data publikacji")
    description = models.TextField(verbose_name="Opis")
    page_count = models.IntegerField(verbose_name="Liczba stron")
    image = models.ImageField(default='default.jpg', upload_to='book_pics')
    slug = AutoSlugField(populate_from='title', null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Książka"
        verbose_name_plural = "Książki"


class BookInstance(models.Model):
    STATUS_CHOICES = [
        ('available', 'Dostępna'),
        ('borrowed', 'Wypożyczona'),
        ('reserved', 'Zarezerwowana'),
        ('maintenance', 'W konserwacji'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    id_code = models.CharField(max_length=6, unique=True, null=True, blank=True, verbose_name="Kod książki",
                               help_text="6 cyfrowy kod książki")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Status książki")

    def __str__(self):
        return f"{self.book} - {self.id_code}"

    class Meta:
        verbose_name = "Egzemplarz książki"
        verbose_name_plural = "Egzemplarze książek"

    def save(self, *args, **kwargs):
        if not self.id_code:
            self.id_code = self.generate_unique_id_code()
        super().save(*args, **kwargs)

    def generate_unique_id_code(self):
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            if not BookInstance.objects.filter(id_code=code).exists():
                return code


# class Loan(models.Model):
#     book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE, verbose_name="Egzemplarz książki")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
#     loan_date = models.DateTimeField(auto_now_add=True, verbose_name="Data wypożyczenia")
#     due_date = models.DateField(verbose_name="Termin zwrotu")  # Zmiana na DateField
#     returned = models.BooleanField(default=False, verbose_name="Zwrócono")
#     returned_date = models.DateTimeField(null=True, blank=True, verbose_name="Data zwrotu")
#
#
#     def save(self, *args, **kwargs):
#         # Przy zapisie, jeśli to nowe wypożyczenie, tworzymy operację
#         if not self.pk:
#             super().save(*args, **kwargs)  # Zapisujemy najpierw, aby uzyskać ID wypożyczenia
#             Operation.objects.create(
#                 book_instance=self.book_instance,
#                 user=self.user,
#                 operation_type='borrow',
#                 loan=self
#             )
#         else:
#             super().save(*args, **kwargs)
#
#         # Zmieniamy status książki na 'borrowed' tylko, jeśli nie została jeszcze zwrócona
#         if not self.returned:
#             self.book_instance.status = 'borrowed'
#             self.book_instance.save()
#
#     def __str__(self):
#         return f"{self.user} wypożyczył {self.book_instance} (do {self.due_date})"
#
#     class Meta:
#         verbose_name = "Wypożyczenie"
#         verbose_name_plural = "Wypożyczenia"

class Loan(models.Model):
    MAX_LOANS = 5  # Maksymalna liczba wypożyczeń dla użytkownika

    book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE, verbose_name="Egzemplarz książki")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    loan_date = models.DateTimeField(auto_now_add=True, verbose_name="Data wypożyczenia")
    due_date = models.DateField(verbose_name="Termin zwrotu")
    returned = models.BooleanField(default=False, verbose_name="Zwrócono")
    returned_date = models.DateTimeField(null=True, blank=True, verbose_name="Data zwrotu")

    def save(self, *args, **kwargs):
        # Dodaj operację wypożyczenia przy tworzeniu nowego rekordu
        if not self.pk:
            super().save(*args, **kwargs)  # Zapisz, aby uzyskać ID wypożyczenia
            Operation.objects.create(
                book_instance=self.book_instance,
                user=self.user,
                operation_type='borrow',
                loan=self
            )
        else:
            super().save(*args, **kwargs)

        # Zmień status książki na 'borrowed', jeśli nie została zwrócona
        if not self.returned:
            self.book_instance.status = 'borrowed'
            self.book_instance.save()

    def __str__(self):
        return f"{self.user} wypożyczył {self.book_instance} (do {self.due_date})"

    class Meta:
        verbose_name = "Wypożyczenie"
        verbose_name_plural = "Wypożyczenia"


class Operation(models.Model):
    OPERATION_TYPE_CHOICES = [
        ('borrow', 'Wypożyczenie'),
        ('return', 'Zwrot'),
    ]

    book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE, verbose_name="Egzemplarz książki")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPE_CHOICES, verbose_name="Typ operacji")
    operation_date = models.DateTimeField(auto_now_add=True, verbose_name="Data operacji")
    loan = models.ForeignKey(Loan, null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name="Powiązane wypożyczenie",
                             help_text="ID wypożyczenia dla operacji wypożyczenia lub zwrotu")

    def clean(self):
        if self.operation_type == 'return':
            if self.book_instance.status != 'borrowed':
                raise ValidationError(
                    f"Książka '{self.book_instance}' nie została wypożyczona, więc nie można jej zwrócić.")
            if not self.loan:
                raise ValidationError("Operacja zwrotu wymaga przypisanego wypożyczenia.")
            if self.loan.user != self.user:
                raise ValidationError("Tylko użytkownik, który wypożyczył książkę, może ją zwrócić.")

    def save(self, *args, **kwargs):
        # Walidacja przed zapisem
        self.clean()

        if self.operation_type == 'return':
            # Zaktualizuj status książki na 'available'
            self.book_instance.status = 'available'
            self.book_instance.save()

            # Oznacz wypożyczenie jako zwrócone
            if self.loan:
                self.loan.returned = True
                self.loan.returned_date = timezone.now()
                self.loan.save()

        # Zapisz operację
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.get_operation_type_display()} - {self.book_instance}"

    class Meta:
        verbose_name = "Operacja"
        verbose_name_plural = "Operacje"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Książka")
    content = models.TextField(max_length=256, verbose_name="Treść komentarza")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    is_read = models.BooleanField(default=False, verbose_name="Przeczytana")  # Dodane pole

    def __str__(self):
        return f"{self.user} - {self.book.title} - {self.created_at}"
