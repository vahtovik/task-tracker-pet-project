from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from users.forms import LoginUserForm, RegisterUserForm


def register_user(request):
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


def edit_credentials(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        form = LoginUserForm(data={'username': login, 'password': password})
        if form.is_valid():
            user = request.user
            user.username = login
            user.set_password(password)
            user.save()
            logout(request)
            return redirect('users:login')
        else:
            return JsonResponse({'success': False, 'error': 'Form validation error'}, status=400)
