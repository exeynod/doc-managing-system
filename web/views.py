# Create your views here.
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.models import User


def index(request):
    return render(request, 'web/index.html', context={'user': request.user})


def log_in(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
    return HttpResponsePermanentRedirect("/web")


def log_out(request):
    logout(request)
    return HttpResponsePermanentRedirect("/web")


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        User.objects.create_user(username, email, password)
    return log_in(request)
