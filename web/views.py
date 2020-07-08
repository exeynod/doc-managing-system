import mimetypes
import os
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.auth import get_user
from django.conf import settings
from django.http import HttpResponse
from .models import Document, DiscussionText
from datetime import datetime
from pathlib import Path
from documents.factory_document import Creator
from django.contrib.auth.decorators import permission_required

extensions = ['.pdf', '.docx']


def index(request, alert=None):
    groups = Group.objects.all()
    context = {'companies': groups, 'alert': alert}
    return render(request, 'web/main.html', context=context)


def check_logged_in(request):
    user = get_user(request)
    if isinstance(user, AnonymousUser):
        return render(request, 'web/errors.html', context={'errno': '403'})
    return user


def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.profile.approved:
                context = {'text': 'Пожалуйста, подождите,'
                                   ' пока администратор группы подтвердит Ваш аккаунт'}
                return render(request, 'web/errors.html', context)
            login(request, user)
        else:
            context = {'text': 'Неверный логин или пароль'}
            return render(request, 'web/errors.html', context)
        return redirect('web:cabinet')
    context = {'text': 'Повторите вход'}
    return render(request, 'web/errors.html', context)


def log_out(request):
    logout(request)
    return redirect('web:index')


def signup(request):
    if request.method != 'POST':
        return render(request, 'web/errors.html', context={'errno': '403'})
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    group_name = request.POST.get('select-company')
    user_exists = User.objects.filter(username=username).count() != 0
    email_exists = User.objects.filter(email=email).count() != 0
    if user_exists:
        return index(request, alert='Пользователь с таким именем уже существует')
    if email_exists:
        return index(request, alert='Пользователь с таким email уже существует')
    group = Group.objects.get(name=group_name)
    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)
    user.groups.set([group])
    user.profile.notifications = ''
    user.profile.approved = False
    user.save()
    return redirect('web:index')


def new_post(request):
    user = get_user(request)
    notifications = user.profile.get_notifications()
    persons = user.profile.get_group_persons()
    context = {'username': user.username, 'notifications': notifications, 'persons': persons}
    return render(request, 'web/add-new-post.html', context)


def user_directory_path(user):
    return '{0}/user_{1}/'.format(settings.MEDIA_ROOT, user.id)


def handle_uploaded_file(user, file, filename):
    path = user_directory_path(user)
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(path + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def delete_old_file(user, filename):
    path = user_directory_path(user) + filename
    Path(path).unlink(missing_ok=True)


def notify_users(request, text, document):
    recipient_counter = 1
    signs_number = 0
    while True:
        recipient = request.POST.get('selectUser-' + str(recipient_counter))
        recipient_counter += 1
        if recipient is None:
            break
        if str(recipient) == 'Выберите пользователя':
            continue
        signs_number += 1
        # Добавить получателям файл в список файлов на подписание
        rec = User.objects.get(username=recipient)
        # Вписываем уведомления пользователя
        rec_notifications = str(rec.profile.notifications)
        rec_notifications += text.format(document.filename)
        rec.profile.notifications = rec_notifications
        rec.profile.files_to_contrib.add(document)
        rec.save()
    return signs_number


def add_new_document(request):
    if request.method != 'POST':
        return render(request, 'web/errors.html', context={'errno': '403'})
    user = check_logged_in(request)
    ext = request.FILES.get('file').name.split('.')[-1]
    filename = str(request.POST.get('Filename')).replace(' ', '') + '.' + ext
    description = request.POST.get('description')
    if str(description) == '<br>':
        description = 'Описание отсутствует'
    deadline = request.POST.get('Date')
    filepath = user_directory_path(user)
    d = Document.objects.create(filename=filename, filepath=filepath, date=deadline, description=description)
    user.profile.personal_files.add(d)
    user.save()
    path = user_directory_path(user) + filename
    d.signs_number = notify_users(request, 'Файл {} был добавлен в список на подписание', d)
    d.signed = 0
    d.save()
    handle_uploaded_file(user, request.FILES.get('file'), filename)
    # setup file in order to lately use it
    Creator.create(path_to_file=path, user_id=str(user.id), primary=True)
    return redirect('web:cabinet')


def my_404_handler(request, exception):
    context = {'errno': '404'}
    return render(request, 'web/errors.html', context)


def my_500_handler(request):
    context = {'errno': '500'}
    return render(request, 'web/errors.html', context)


def csrf_failure(request, reason=""):
    context = {'errno': '403', 'text': reason}
    return render(request, 'web/errors.html', context)


def review(request, filename):
    user = get_user(request)
    notifications = user.profile.get_notifications()
    personal_context = user.profile.get_statistic()
    discussions = DiscussionText.objects.filter(document__filename=filename)
    file = Document.objects.filter(filename=filename) \
        .filter(Q(owner__user__username=user.username) | Q(reviewer__user__username=user.username))[0]
    owner = file.owner.all()[0]
    reviewer = User.objects.filter(username=user.username).filter(profile__files_to_contrib=file.id).count() != 0
    path = user_directory_path(owner) + filename
    if '/app' in path:
        path = path.replace('/app', '.')
    sd = Creator.create(user_id=str(user.id), path_to_file=path, primary=False)
    if owner.id == user.id:
        signs = [User.objects.get(id=sign_id) for sign_id in sd.who_signed()]
    else:
        signs = None
    context = {'username': user.username, 'discussions': discussions,
               'filename': filename, 'file_date': file.date,
               'description': file.description, 'owner': owner.id == user.id,
               'reviewer': reviewer, 'status': str(file.status),
               'signed': sd.who_signed().count(user.id) != 0, 'signs': signs,
               'notifications': notifications}
    context.update(personal_context)
    return render(request, 'web/document_review.html', context)


def new_review(request, filename):
    author = get_user(request)
    username = author.username
    description = request.POST.get('description')
    publish_date = datetime.now().date()
    document = Document.objects.filter(filename=filename) \
        .filter(Q(owner__user__username=username) | Q(reviewer__user__username=username))[0]
    discussion = DiscussionText.objects.create(author=author.username, description=description,
                                               publish_date=publish_date, document=document)
    discussion.save()
    return redirect('web:document_review', filename)


def download(request, filename):
    user = get_user(request)
    file = user_directory_path(user) + filename
    with open(file, 'rb') as f:
        response = HttpResponse(f.read())
        file_type = mimetypes.guess_type(file)
        if file_type is None:
            file_type = 'application/octet-stream'
        response['Content-Type'] = file_type
        response['Content-Length'] = str(os.stat(file).st_size)
        response['Content-Disposition'] = f"attachment; filename={filename}"
    return response


def user_page(request):
    user = check_logged_in(request)
    notifications = user.profile.get_notifications()
    context = {'username': user.username, 'email': user.email, 'notifications': notifications}
    return render(request, 'web/user-profile-lite.html', context=context)


def update_account(request):
    user = check_logged_in(request)
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    user.profile.update(username, email, password)
    notifications = user.profile.get_notifications()
    context = {'username': username, 'email': user.email, 'notifications': notifications}
    return render(request, 'web/user-profile-lite.html', context=context)


def show_documents(request):
    user = get_user(request)
    notifications = user.profile.get_notifications()
    personal_context = user.profile.get_statistic()
    context = {'username': user.username, 'notifications': notifications}
    context.update(personal_context)
    return render(request, 'web/tables.html', context=context)


def search(request):
    user = get_user(request)
    notifications = user.profile.get_notifications()
    text = request.POST.get('text')
    personal_context = user.profile.get_statistic()
    files_found = [Document.objects.filter(filename=text + ext).filter(Q(owner__user__username=user.username) |
                                                                       Q(reviewer__user__username=user.username))
                   for ext in extensions]
    context = {'username': user.username, 'notifications': notifications, 'files_found': files_found}
    context.update(personal_context)
    return render(request, 'web/search.html', context=context)


def edit_document(request, filename):
    user = get_user(request)
    notifications = user.profile.get_notifications()
    file = Document.objects.filter(filename=filename). \
        filter(Q(owner__user__username=user.username) | Q(reviewer__user__username=user.username))[0]
    recipients = User.objects.filter(profile__files_to_contrib=file.id)
    recipient_names = list()
    persons = user.profile.get_group_persons()
    for rec in recipients:
        recipient_names.append(rec.username)
        persons.remove(rec.username)
    context = {'username': user.username, 'notifications': notifications, 'persons': persons,
               'filename': filename, 'recipients': recipient_names,
               'deadline': str(file.date)}
    return render(request, 'web/edit-document.html', context)


def apply_edits(request, filename):
    user = check_logged_in(request)
    recipient_counter = 1
    new_name = request.POST.get('Filename')
    description = request.POST.get('description')
    deadline = request.POST.get('Date')
    file = Document.objects.filter(filename=filename).filter(owner__user_id=user.id)[0]
    if new_name:
        path = user_directory_path(user)
        p = Path(path + filename)
        p.rename(path + new_name)
        file.filename = new_name
    if description:
        file.description = description
    if deadline:
        file.date = deadline
    new_file = request.FILES.get('file')
    if new_file:
        ext = request.FILES.get('file').name.split('.')[-1]
        new_name = new_name + '.' + ext
        delete_old_file(user, filename)
        handle_uploaded_file(user, new_file, new_name)
    file.save()
    signs_number = notify_users(request, 'Файл {} был изменен\n', file)
    if signs_number != file.signs_number:
        owner = file.owner.all()[0]
        path = user_directory_path(owner) + filename
        sd = Creator.create(user_id=str(user.id), path_to_file=path, primary=False)
        file.signed = len(sd.who_signed())
        file.signs_number = recipient_counter
        file.status = 'В процессе'
    return redirect('web:document_review', new_name)


def sign(request, filename):
    user = check_logged_in(request)
    file = Document.objects.filter(filename=filename). \
        filter(Q(owner__user__username=user.username) | Q(reviewer__user__username=user.username))[0]
    file.signed += 1
    owner = file.owner.all()[0]
    if file.signed >= file.signs_number:
        file.status = 'Готов'
        owner.notifications += 'Файл ' + filename + ' подписан\n'
        owner.save()
    file.save()
    path = user_directory_path(owner) + filename
    sd = Creator.create(user_id=str(user.id), path_to_file=path, primary=False)
    signed = sd.is_signed_by()
    if not signed:
        sd.sign()
    return redirect('web:document_review', filename)


def cancel(request, filename):
    user = check_logged_in(request)
    file = Document.objects.filter(filename=filename). \
        filter(Q(owner__user__username=user.username) | Q(reviewer__user__username=user.username))[0]
    file.status = 'Отменен'
    file.signed = 0
    file.save()
    owner = file.owner.all()[0]
    owner.notifications += 'Файл ' + filename + ' был не принят пользователем ' + user.username + '\n'
    owner.save()
    return redirect('web:document_review', filename)


def certbot_auth(*args, **kwargs):
    return HttpResponse('wl02Bwi2-dCe4gkHdf5kP0XM3m-kuKq8WgVMjGvv2AM.BR9XYxef6ASNw28tTqRyB8aLg2syKH2-cqk8ZnUtr_s')


@permission_required('auth.change_group')
def approve(request, username):
    approve_user = User.objects.get(username=username)
    approve_user.profile.approved = True
    approve_user.save()
    return redirect('web:group')


@permission_required('auth.view_group')
def group_review(request):
    user = get_user(request)
    group = Group.objects.filter(name=user.groups.first())[0]
    persons = User.objects.filter(groups=group).filter(~Q(username=user.username))
    user = get_user(request)
    notifications = user.profile.get_notifications()
    context = {'username': user.username, 'notifications': notifications, 'persons': persons}
    return render(request, 'web/group.html', context=context)


@permission_required('auth.change_group')
def remove_user(request, username):
    user_to_delete = User.objects.get(username=username)
    user_to_delete.delete()
    return redirect('web:group')
