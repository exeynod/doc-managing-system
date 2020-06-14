# Create your views here.
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.models import User, Group


def index(request):
    groups = Group.objects.all()
    context = {'companies': groups}
    return render(request, 'web/main.html', context=context)


def log_in(request):
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    user = authenticate(username=email, password=password)
    if user is not None:
        login(request, user)
    return render(request, 'web/index.html')


def log_out(request):
    logout(request)
    return HttpResponsePermanentRedirect("/web")


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        User.objects.create_user(email, password)
    return log_in(request)