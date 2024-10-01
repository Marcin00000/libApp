from django.db import models
from django.urls import reverse


# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Imię")
    surname = models.CharField(max_length=100, verbose_name="Nazwisko")

    def __str__(self):
        return self.name + " " + self.surname

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autorzy"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoria")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"


class Publisher(models.Model):
    name = models.CharField(max_length=100, verbose_name="Wydawca")

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
    publication_date = models.DateField( verbose_name="Data publikacji")
    description = models.TextField( verbose_name="Opis")
    page_count = models.IntegerField( verbose_name="Liczba stron")
    # image_url = models.URLField()


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Książka"
        verbose_name_plural = "Książki"