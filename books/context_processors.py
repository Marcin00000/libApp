from .models import Loan
from django.db.models import Count



def borrowed_count(request):
    if request.user.is_authenticated:
        count = Loan.objects.filter(user=request.user, returned=False).count()  # Licz tylko wypożyczone książki
        return {'borrowed_count': count}
    return {'borrowed_count': 0}


def read_books_count(request):
    if request.user.is_authenticated:
        read_count = Loan.objects.filter(user=request.user, returned=True).count()
        return {'read_count': read_count}
    return {'read_count': 0}  # Zwróć 0, jeśli użytkownik nie jest zalogowany
