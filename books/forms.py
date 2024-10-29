from django import forms

class BorrowBookForm(forms.Form):
    id_code = forms.CharField(max_length=6, label="Kod książki", help_text="Wprowadź 6-cyfrowy kod egzemplarza książki")
