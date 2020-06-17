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
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
    # Вписываем уведомления пользователя
    if user is None:
        return render(request, 'web/errors.html')
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
        groupName = request.POST.get('select-company')
        group = Group.objects.get(name=groupName)
        user = User.objects.create_user(email, password)
        user.groups.set([group])
        user.save()
    return redirect('web:login')


def new_post(request):
    user = get_user(request)
    if user is not AnonymousUser:
        # Вписываем уведомления пользователя
        username = user.username
        notifications = user.profile.notifications
        persons = list()
        for group in user.groups.all():
            users = User.objects.filter(groups=Group.objects.get(name=group.name))
            for user in users:
                persons.append(user.username)
        context = {'username': username, 'notifications': notifications, 'persons': persons}
        return render(request, 'web/add-new-post.html', context)
    return render(request, 'web/errors.html')