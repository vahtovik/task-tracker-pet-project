from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='', widget=forms.TextInput(), required=True, error_messages={
        'required': 'Поле обязательно для заполнения',
    })
    password = forms.CharField(label='', widget=forms.PasswordInput(), required=True, error_messages={
        'required': 'Поле обязательно для заполнения',
    })

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='', widget=forms.TextInput(), required=True, error_messages={
        'required': 'Поле обязательно для заполнения',
        'unique': 'Пользователь с таким именем уже существует',
    })
    password1 = forms.CharField(label='', widget=forms.PasswordInput(), required=True, error_messages={
        'required': 'Поле обязательно для заполнения',
    })
    password2 = forms.CharField(label='', widget=forms.PasswordInput(), required=True, error_messages={
        'required': 'Поле обязательно для заполнения',
    })

    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error('password1', '')
            raise forms.ValidationError('Пароли не совпадают', code='password_mismatch')
        return password2
