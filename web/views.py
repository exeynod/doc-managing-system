# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.auth import get_user
from django.conf import settings
from .models import Document
from datetime import date, datetime, timedelta
from pathlib import Path


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
    # Заполним шапку с числоп документов
    username = user.username
    notifications = str(user.profile.notifications).split('\n')
    notifications.remove('')
    user.profile.notifications = ''
    user.save()
    deadlines_count = 0
    personal_files = str(user.profile.personal_files).split('\n')
    personal_files.remove('')
    files_to_contrib = str(user.profile.files_to_contrib).split('\n')
    files_to_contrib.remove('')
    for document in files_to_contrib:
        deadline = date.fromisoformat(str(Document.objects.get(filename=document).date))
        if deadline - datetime.now().date() <= timedelta(days=1):
            deadlines_count += 1
    context = {'username': username, 'notifications': notifications, 'deadlines': deadlines_count,
               'files_to_sign': len(files_to_contrib), 'personal_files': len(personal_files)}
    return render(request, 'web/index.html', context=context)


def log_out(request):
    logout(request)
    return redirect('web:index')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        groupName = request.POST.get('select-company')
        group = Group.objects.get(name=groupName)
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        user.groups.set([group])
        user.profile.personal_files = ''
        user.profile.files_to_contrib = ''
        user.profile.notifications = ''
        user.save()
    return redirect('web:login')


def new_post(request):
    user = get_user(request)
    if user is not AnonymousUser:
        # Вписываем уведомления пользователя
        username = user.username
        notifications = str(user.profile.notifications).split('\n')
        notifications.remove('')
        persons = set()
        for group in user.groups.all():
            users = User.objects.filter(groups=Group.objects.get(name=group.name))
            for user in users:
                persons.add(user.username)
        context = {'username': username, 'notifications': notifications, 'persons': persons}
        return render(request, 'web/add-new-post.html', context)
    return render(request, 'web/errors.html')


def user_directory_path(user):
    return '{0}/user_{1}/'.format(settings.MEDIA_ROOT, user.id)


def handle_uploaded_file(user, file, filename):
    path = user_directory_path(user)
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(path + filename + '.pdf', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def add_new_post(request):
    user = get_user(request)
    if user is not AnonymousUser and request.method == 'POST':
        recipients = list()
        recipient_counter = 1
        filename = request.POST.get('Filename')
        description = request.POST.get('description')
        deadline = request.POST.get('Date')
        filepath = user_directory_path(user)
        while True:
            recipient = request.POST.get('selectUser-' + str(recipient_counter))
            recipient_counter += 1
            if recipient is None:
                break
            if str(recipient) == 'Choose recipients':
                continue
            recipients.append(str(recipient) + '\n')
            # Добавить получателям файл в список файлов на подписание
            rec = User.objects.get(username=recipient)
            rec_files_to_contrib = str(rec.profile.files_to_contrib)
            rec_files_to_contrib += str(filename) + '\n'
            rec.profile.files_to_contrib = rec_files_to_contrib
            # Вписываем уведомления пользователя
            rec_notifications = str(rec.profile.notifications)
            rec_notifications += 'File ' + filename + 'added to your sign list\n'
            rec.profile.notifications = rec_notifications
            rec.save()

        d = Document(filename=filename, filepath=filepath, date=deadline, users=recipients, description=description)
        d.save()

        # Добавим файл в список файлов пользователя
        personal_files = user.profile.personal_files
        personal_files += filename + '\n'
        user.profile.personal_files = personal_files
        user.save()

        handle_uploaded_file(user, request.FILES.get('file'), filename)
        return redirect('web:login')
    return render(request, 'web/errors.html')


def my_404_handler(request, exception):
    context = {'errno': '404'}
    return render(request, 'web/errors.html', context)


def my_500_handler(request):
    context = {'errno': '500'}
    return render(request, 'web/errors.html', context)


def csrf_failure(request, reason=""):
    context = {'errno': '403'}
    return render(request, 'web/errors.html', context)


def review(request):
    context = {}
    return render(request, 'web/document_review.html', context)


