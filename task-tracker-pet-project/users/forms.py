from django import forms
from django.contrib.auth import get_user_model, password_validation, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Введите логин'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                self.add_error('username', '')
                self.add_error('password', '')
                raise forms.ValidationError('Неверный логин или пароль.')

        return super().clean()


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Введите логин'}))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            self.add_error('password1', '')
        try:
            password_validation.validate_password(password1)
        except forms.ValidationError as error:
            self.add_error('password1', '')
        if password1.isdigit():
            self.add_error('password1', '')

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error('password1', '')
            raise forms.ValidationError('Пароли не совпадают.', code='password_mismatch')
        return password2


class ChangeLoginAndPasswordForm(forms.Form):
    username = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'Новый логин'}))
    new_password1 = forms.CharField(label='', required=False,
                                    widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'}))
    new_password2 = forms.CharField(label='', required=False,
                                    widget=forms.PasswordInput(attrs={'placeholder': 'Повторите новый пароль'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password2:
            try:
                password_validation.validate_password(new_password2)
            except forms.ValidationError as error:
                self.add_error('new_password1', ' ')
                self.cleaned_data['new_password1'] = new_password1
                raise forms.ValidationError(error)

        return new_password2

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                self.add_error('new_password1', ' ')
                self.add_error('new_password2', 'Пароли не совпадают.')

        if new_password1 and not new_password2:
            self.add_error('new_password2', 'Обязательное поле.')

        if not new_password1 and new_password2:
            self.add_error('new_password1', 'Обязательное поле.')

        return cleaned_data
