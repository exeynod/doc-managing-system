# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.auth import get_user


def index(request):
    groups = Group.objects.all()
    context = {'companies': groups}
    return render(request, 'web/main.html', context=context)


def log_in(request):
    user = get_user(request)
    if user is AnonymousUser:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return render(request, 'web/errors.html')
    # Вписываем уведомления пользователя
    username = user.username
    notifications = user.profile.notifications
    context = {'username': username, 'notifications': notifications}
    return render(request, 'web/index.html', context=context)


def log_out(request):
    logout(request)
    return redirect('web:index')


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        User.objects.create_user(email, password)
    return log_in(request)


def new_post(request):
    user = get_user(request)
    if user is not AnonymousUser:
        # Вписываем уведомления пользователя
        username = user.username
        notifications = user.profile.notifications
        context = {'username': username, 'notifications': notifications}
        return render(request, 'web/add-new-post.html', context)
    return render(request, 'web/errors.html')