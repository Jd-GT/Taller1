from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES, label="Tipo de usuario")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
        labels = {
            'username': 'Usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        error_messages = {
            'username': {
                'required': "El nombre de usuario es obligatorio.",
                'unique': "Este nombre de usuario ya está en uso.",
            },
            'email': {
                'required': "El correo electrónico es obligatorio.",
                'invalid': "Introduce un correo electrónico válido.",
            },
            'password1': {
                'required': "La contraseña es obligatoria.",
                'password_too_short': "La contraseña debe tener al menos 8 caracteres.",
                'password_too_common': "La contraseña es demasiado común, elige otra.",
                'password_entirely_numeric': "La contraseña no puede contener solo números.",
            },
            'password2': {
                'required': "Debes confirmar tu contraseña.",
                'password_mismatch': "Las contraseñas no coinciden.",
            },
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.create(user=user, user_type=self.cleaned_data['user_type'])
        return user

