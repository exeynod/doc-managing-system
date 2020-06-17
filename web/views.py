# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group


def index(request):
    groups = Group.objects.all()
    context = {'companies': groups}
    return render(request, 'web/main.html', context=context)


def log_in(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        # Вписываем уведомления пользователя
        notifications = user.profile.notifications
        context = {'username': username, 'notifications': notifications}
        return render(request, 'web/index.html', context=context)
    return render(request, 'web/errors.html')


def log_out(request):
    logout(request)
    return redirect('web:index')


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        User.objects.create_user(email, password)
    return log_in(request)


def add_new_document(request):
    pass


def add_new_document_page(request):
    return render(request, 'web:add-new-post.html')