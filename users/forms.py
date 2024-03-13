from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='', widget=forms.TextInput(
        attrs={'class': 'input auth__input', 'placeholder': 'Введите логин'}))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'class': 'input auth__input', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'class': 'input auth__input', 'placeholder': 'Повторите пароль'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')


class LoginUserForm(forms.Form):
    username = forms.CharField(label='', widget=forms.TextInput(
        attrs={'class': 'input auth__input', 'placeholder': 'Введите логин'}), required=False)
    password = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'class': 'input auth__input', 'placeholder': 'Введите пароль'}), required=False)

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')
