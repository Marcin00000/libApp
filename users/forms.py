from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from users.models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(label="Imię")
    last_name = forms.CharField(label="Nazwisko")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name' , 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Podany adres email jest już zarejestrowany.")
        return email


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(label="Imię")
    last_name = forms.CharField(label="Nazwisko")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id  # Pobiera aktualnego użytkownika, który jest aktualizowany

        # Sprawdzenie, czy email już istnieje, ale ignorujemy bieżącego użytkownika
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError("Podany adres email jest już używany przez innego użytkownika.")

        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
