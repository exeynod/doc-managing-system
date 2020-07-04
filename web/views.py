# Create your views here.
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
from datetime import date, datetime, timedelta
from pathlib import Path
from documents import document as Sign_Document
from django.contrib.auth.decorators import permission_required


def index(request, alert=None):
    groups = Group.objects.all()
    context = {'companies': groups, 'alert': alert}
    return render(request, 'web/main.html', context=context)


def check_logged_in(request):
    user = get_user(request)
    if isinstance(user, AnonymousUser):
        return render(request, 'web/errors.html', context={'errno': '403'})
    return user


def get_statistics(request):
    user = check_logged_in(request)
    # Заполним шапку с числоп документов
    username = user.username
    notifications = str(user.profile.notifications).split('\n')
    notifications.remove('')
    user.profile.notifications = ''
    user.save()
    deadlines_count = 0
    personal_files = Document.objects.filter(owner__user__username=username)
    if personal_files:
        personal_files_len = personal_files.count()
    else:
        personal_files_len = 0
    files_to_contrib = Document.objects.filter(reviewer__user__username=username).filter(status='В процессе')
    if files_to_contrib:
        files_to_contrib_len = files_to_contrib.count()
        for document in files_to_contrib:
            deadline = date.fromisoformat(str(document.date))
            if deadline - datetime.now().date() <= timedelta(days=1) and document.status != 'Готов':
                deadlines_count += 1
    else:
        files_to_contrib_len = 0
    return user, notifications, deadlines_count, files_to_contrib_len, \
           personal_files_len, personal_files, files_to_contrib


def get_username_notification_persons(request):
    user = check_logged_in(request)
    # Вписываем уведомления пользователя
    username = user.username
    notifications = str(user.profile.notifications).split('\n')
    notifications.remove('')
    persons = set()
    for group in user.groups.all():
        users = User.objects.filter(groups=Group.objects.get(name=group.name))
        for user in users:
            persons.add(user.username)
    return username, notifications, persons


def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None and user.profile.approved:
            login(request, user)
        else:
            return render(request, 'web/errors.html')
    return redirect('web:cabinet')


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
    user.groups.set([group])
    user.profile.notifications = ''
    user.save()
    login(request, user)
    return redirect('web:login')


def new_post(request):
    username, notifications, persons = get_username_notification_persons(request)
    context = {'username': username, 'notifications': notifications, 'persons': persons}
    return render(request, 'web/add-new-post.html', context)


def user_directory_path(user):
    return '{0}/user_{1}/'.format(settings.MEDIA_ROOT, user.id)


def handle_uploaded_file(user, file, filename):
    path = user_directory_path(user)
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(path + filename + '.pdf', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def delete_old_file(user, filename):
    path = user_directory_path(user) + filename + '.pdf'
    Path(path).unlink(missing_ok=True)


def add_new_document(request):
    user = get_user(request)
    if isinstance(user, AnonymousUser) or request.method != 'POST':
        return render(request, 'web/errors.html', context={'errno': '403'})
    recipients = list()
    recipient_counter = 1
    signs_number = 0
    filename = str(request.POST.get('Filename')).replace(' ', '')
    description = request.POST.get('description')
    if str(description) == '<br>':
        description = 'Описание отсутствует'
    deadline = request.POST.get('Date')
    filepath = user_directory_path(user)
    d = Document.objects.create(filename=filename, filepath=filepath, date=deadline, description=description)
    user.profile.personal_files.add(d)
    user.save()
    path = user_directory_path(user) + filename + '.pdf'
    while True:
        recipient = request.POST.get('selectUser-' + str(recipient_counter))
        recipient_counter += 1
        if recipient is None:
            break
        if str(recipient) == 'Выберите пользователя':
            continue
        signs_number += 1
        recipients.append(str(recipient) + '\n')
        # Добавить получателям файл в список файлов на подписание
        rec = User.objects.get(username=recipient)
        # Вписываем уведомления пользователя
        rec_notifications = str(rec.profile.notifications)
        rec_notifications += 'Файл ' + filename + ' был добавлен в список документов на подпись\n'
        rec.profile.notifications = rec_notifications
        rec.profile.files_to_contrib.add(d)
        rec.save()
    d.signs_number = signs_number
    d.signed = 0
    d.save()
    handle_uploaded_file(user, request.FILES.get('file'), filename)
    Sign_Document.Document(user_id=str(user.id), path=path, primary=True)
    return redirect('web:login')


def my_404_handler(request, exception):
    context = {'errno': '404'}
    return render(request, 'web/errors.html', context)


def my_500_handler(request):
    context = {'errno': '500'}
    return render(request, 'web/errors.html', context)


def csrf_failure(request, reason=""):
    context = {'errno': '403'}
    return render(request, 'web/errors.html', context)


def review(request, filename):
    user, notifications, deadlines_count, files_to_contrib_len, personal_files_len, *_ = get_statistics(request)
    discussions = DiscussionText.objects.filter(document__filename=filename)
    file = Document.objects.filter(filename=filename) \
        .filter(Q(owner__user__username=user.username) | Q(reviewer__user__username=user.username))[0]
    owner = file.owner.all()[0]
    reviewer = User.objects.filter(username=user.username).filter(profile__files_to_contrib=file.id) != 0
    path = user_directory_path(owner) + filename + '.pdf'
    if '/app' in path:
        path = path.replace('/app', '.')
    sd = Sign_Document.Document(user_id=str(user.id), path=path, primary=False)
    signed = sd.is_signed_by()
    if owner.id == user.id:
        signs_id = sd.who_signed()
        signs = list()
        for sign_id in signs_id:
            signs.append(User.objects.get(id=sign_id).username)
    else:
        signs = None
    context = {'username': user.username, 'notifications': notifications, 'deadlines': deadlines_count,
               'files_to_sign': files_to_contrib_len, 'personal_files': personal_files_len,
               'discussions': discussions, 'filename': filename, 'file_date': file.date,
               'description': file.description, 'owner': owner.id == user.id, 'reviewer': reviewer,
               'status': str(file.status), 'signed': signed, 'signs': signs}
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
    file = user_directory_path(user) + filename + '.pdf'
    with open(file, 'rb') as f:
        response = HttpResponse(f.read())
        file_type = mimetypes.guess_type(file)
        if file_type is None:
            file_type = 'application/octet-stream'
        response['Content-Type'] = file_type
        response['Content-Length'] = str(os.stat(file).st_size)
        response['Content-Disposition'] = f"attachment; filename={filename}.pdf"
    return response


def user_page(request):
    user = check_logged_in(request)
    notifications = str(user.profile.notifications).split('\n')
    notifications.remove('')
    context = {'username': user.username, 'email': user.email, 'notifications': notifications}
    return render(request, 'web/user-profile-lite.html', context=context)


def update_account(request):
    user = get_user(request)
    if request.method != 'POST' or isinstance(user, AnonymousUser):
        return render(request, 'web/errors.html', context={'errno': '403'})
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    user.username = username
    user.email = email
    if password:
        user.set_password(password)
    user.save()
    notifications = str(user.profile.notifications).split('\n')
    notifications.remove('')
    context = {'username': username, 'email': user.email, 'notifications': notifications}
    return render(request, 'web/user-profile-lite.html', context=context)


def show_documents(request):
    user, notifications, deadlines_count, files_to_contrib_len, personal_files_len, \
    personal_files, files_to_contrib = get_statistics(request)
    context = {'username': user.username, 'notifications': notifications, 'deadlines': deadlines_count,
               'files_to_sign': files_to_contrib_len, 'personal_files': personal_files_len,
               'my_files': personal_files, 'review_files': files_to_contrib}
    return render(request, 'web/tables.html', context=context)


def search(request):
    username, notifications, deadlines_count, files_to_contrib_len, personal_files_len, *_ = get_statistics(request)
    text = request.POST.get('text')
    files_found = Document.objects.filter(filename=text). \
        filter(Q(owner__user__username=username) | Q(reviewer__user__username=username))
    context = {'username': username, 'notifications': notifications, 'deadlines': deadlines_count,
               'files_to_sign': files_to_contrib_len, 'personal_files': personal_files_len, 'files_found': files_found}
    return render(request, 'web/search.html', context=context)


def edit_document(request, filename):
    username, notifications, persons = get_username_notification_persons(request)
    file = Document.objects.filter(filename=filename). \
        filter(Q(owner__user__username=username) | Q(reviewer__user__username=username))[0]
    recipients = User.objects.filter(profile__files_to_contrib=file.id)
    recipient_names = list()
    for rec in recipients:
        recipient_names.append(rec.username)
        persons.remove(rec.username)
    context = {'username': username, 'notifications': notifications, 'persons': persons,
               'filename': filename, 'recipients': recipient_names,
               'deadline': str(file.date)}
    return render(request, 'web/edit-document.html', context)


def apply_edits(request, filename):
    user = get_user(request)
    if isinstance(user, AnonymousUser) or request.method != 'POST':
        return render(request, 'web/errors.html', context={'errno': '403'})
    recipients = list()
    recipient_counter = 1
    signs_number = 0
    new_name = request.POST.get('Filename')
    description = request.POST.get('description')
    deadline = request.POST.get('Date')
    file = Document.objects.filter(filename=filename).filter(owner__user_id=user.id)[0]
    if new_name:
        path = user_directory_path(user)
        p = Path(path + filename + '.pdf')
        p.rename(path + new_name + '.pdf')
        file.filename = new_name
    if description:
        file.description = description
    if deadline:
        file.date = deadline
    new_file = request.FILES.get('file')
    if new_file:
        delete_old_file(user, filename)
        handle_uploaded_file(user, new_file, new_name)
    file.save()
    while True:
        recipient = request.POST.get('selectUser-' + str(recipient_counter))
        recipient_counter += 1
        if recipient is None:
            break
        if str(recipient) == 'Выберите пользователя':
            continue
        signs_number += 1
        recipients.append(str(recipient) + '\n')
        # Добавить получателям файл в список файлов на подписание
        rec = User.objects.get(username=recipient)
        # Вписываем уведомления пользователя
        rec_notifications = str(rec.profile.notifications)
        rec_notifications += 'Файл ' + filename + ' был изменен\n'
        rec.profile.notifications = rec_notifications
        rec.save()
    if recipient_counter != file.signs_number:
        owner = file.owner.all()[0]
        path = user_directory_path(owner) + filename + '.pdf'
        sd = Sign_Document.Document(user_id=str(user.id), path=path, primary=False)
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
    path = user_directory_path(owner) + filename + '.pdf'
    sd = Sign_Document.Document(user_id=str(user.id), path=path, primary=False)
    signed = sd.is_signed_by()
    if not signed:
        sd = Sign_Document.Document(user_id=str(user.id), path=path, primary=False)
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
    persons = User.objects.filter(groups=group)
    username, notifications, _ = get_username_notification_persons(request)
    context = {'username': username, 'notifications': notifications, 'persons': persons}
    return render(request, 'web/group.html', context=context)


@permission_required('auth.change_group')
def remove_user(request, username):
    user_to_delete = User.objects.get(username=username)
    user_to_delete.delete()
    return redirect('web:group')