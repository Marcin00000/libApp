from django.db import models

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    def __str__(self):
        return self.name + " " + self.surname


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    ASIN = models.CharField(max_length=11)
    publication_date = models.DateField()
    description = models.TextField()
    page_count = models.IntegerField()
    # image_url = models.URLField()


    def __str__(self):
        return self.title