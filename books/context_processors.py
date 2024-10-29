# books/context_processors.py
from .models import Loan

def borrowed_count(request):
    count = Loan.objects.filter(returned=False).count()  # Licz tylko wypożyczone książki
    return {
        'borrowed_count': count
    }
