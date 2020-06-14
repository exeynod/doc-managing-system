# Create your views here.
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.models import User


def index(request):
    return render(request, 'web/main.html')


def log_in(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
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
