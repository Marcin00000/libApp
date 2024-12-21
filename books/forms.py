from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

from books.models import Comment, AuthorComment


class BorrowBookForm(forms.Form):
    id_code = forms.CharField(max_length=6, label="Kod książki", help_text="Wprowadź 6-cyfrowy kod egzemplarza książki")


class CommentForm(forms.ModelForm):
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = Comment
        fields = ['content', 'recaptcha']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'placeholder': 'Dodaj swój komentarz...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Dodaj Komentarz'))


class AuthorCommentForm(forms.ModelForm):
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = AuthorComment
        fields = ['content', 'recaptcha']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'placeholder': 'Dodaj swój komentarz...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Dodaj Komentarz'))
