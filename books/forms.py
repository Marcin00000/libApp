from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from books.models import Comment


class BorrowBookForm(forms.Form):
    id_code = forms.CharField(max_length=6, label="Kod książki", help_text="Wprowadź 6-cyfrowy kod egzemplarza książki")


# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['text']
#         labels = {'text': 'Treść komentarza'}
#         widgets = {'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Dodaj komentarz...'})}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'placeholder': 'Dodaj swój komentarz...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Dodaj Komentarz'))