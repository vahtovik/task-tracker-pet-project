from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from users.forms import LoginUserForm, RegisterUserForm, ChangeLoginAndPasswordForm


def register_user(request):
    if request.user.is_authenticated:
        return redirect('main_app:index')

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('main_app:index')
    else:
        form = RegisterUserForm()

    return render(request, 'users/register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('main_app:index')

    if request.method == 'POST':
        form = LoginUserForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect('main_app:index')
    else:
        form = LoginUserForm()

    return render(request, 'users/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('users:login')


@require_POST
@login_required
def edit_credentials(request):
    form = ChangeLoginAndPasswordForm(request.POST)
    if form.is_valid():
        user = request.user
        username = form.cleaned_data['username']
        new_password = form.cleaned_data['new_password1']
        if username:
            user.username = username
        if new_password:
            user.set_password(new_password)
            # Сохраняем сессию после смены пароля
            update_session_auth_hash(request, user)
        user.save()
        logout(request)
        return JsonResponse({'success': True})
    else:
        errors = {field: form.errors[field][0] for field in form.errors}
        return JsonResponse({'success': False, 'errors': errors})
