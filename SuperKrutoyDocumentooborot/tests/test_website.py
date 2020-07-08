from django.test import TestCase, Client
from django.contrib.auth.models import User, Group, AnonymousUser
from web.models import Document
from datetime import datetime


class WebsiteTest(TestCase):
    c = Client()

    def setUp(self):
        User.objects.create_user(username='Admin', password='admin', email='e@ma.il')

    def login(self):
        self.c.login(username='Admin', password='admin')

    def test_index(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_registration(self):
        Group.objects.create(name='BMSTU')
        context = {'username': 'User0', 'email': 'E@mai.l', 'select-company': 'BMSTU', 'password': 'qwerty'}
        response = self.c.post('/signup/', context)
        self.assertEqual(response.status_code, 302)

    def test_dublicate_username(self):
        User.objects.create_user(username='User1', password='qwerty', email='email')
        self.assertEqual(User.objects.filter(username='User1').count(), 1)
        context = {'username': 'User1', 'email': 'E@mai.l', 'select-company': 'BMSTU', 'password': 'qwerty'}
        self.c.post('/signup/', context)
        self.assertEqual(User.objects.filter(username='User1').count(), 1)

    def test_dublicate_email(self):
        User.objects.create_user(username='User2', password='qwerty', email='E@mai.l')
        self.assertEqual(User.objects.filter(username='User2').count(), 1)
        context = {'username': 'User3', 'email': 'E@mai.l', 'select-company': 'BMSTU', 'password': 'qwerty'}
        self.c.post('/signup/', context)
        self.assertEqual(User.objects.filter(username='User3').count(), 0)

    def test_login(self):
        u = User.objects.create_user(username='User', password='qwerty', email='E@mai.l')
        u.profile.approved = True
        context = {'username': 'User', 'password': 'qwerty'}
        response = self.c.post('/login/', context)
        self.assertEqual(response.status_code, 200)

    def test_bad_login(self):
        context = {'username': 'User5', 'password': '5'}
        response = self.c.post('/login/', context)
        self.assertEqual(response.status_code, 200)

    def test_add_new_post(self):
        self.login()
        file = open('SuperKrutoyDocumentooborot/tests/test_docs/changed.pdf', 'rb')
        context = {'Filename': 'New file',
                   'description': '<br>',
                   'Date': datetime.now().date(),
                   'selectUser-1': 'Admin',
                   'file': file,
                   }
        response = self.c.post('/add-post/', context)
        self.assertEqual(response.status_code, 302)
        d = Document.objects.get(filename='Newfile.pdf', owner__user__username='Admin')
        self.assertEqual(d.filename, 'Newfile.pdf')
        self.assertEqual(d.description, 'Описание отсутствует')
        self.assertEqual(d.status, 'В процессе')
        self.assertEqual(d.signs_number, 1)
        self.assertEqual(d.signed, 0)

    def test_review(self):
        self.test_add_new_post()
        response = self.c.get('/Newfile.pdf/review/')
        c = response.context
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.context['user'], AnonymousUser), 0)
        self.assertEqual(len(c['notifications']), 1)
        self.assertEqual(c['deadlines'], 1)
        self.assertEqual(c['files_to_sign'], 1)
        self.assertEqual(c['personal_files'], 1)
        self.assertEqual(len(c['discussions']), 0)

    def test_new_review(self):
        self.test_add_new_post()
        context = {'description': 'Test edits'}
        self.c.post('/Newfile.pdf/review/new/', context)
        response = self.c.get('/Newfile.pdf/review/')
        c = response.context
        self.assertEqual(len(c['discussions']), 1)

    def test_user_page(self):
        self.login()
        c = self.c.get('/user/').context
        self.assertEqual(c['username'], 'Admin')
        self.assertEqual(c['email'], 'e@ma.il')

    def test_update_account(self):
        self.login()
        context = {'username': 'New_admin', 'email': 'admin@admin.com', 'password': 'pass'}
        self.c.post('/update-account/', context)
        self.c.login(username='New_admin', password='pass')
        c = self.c.get('/user/').context
        self.assertEqual(c['username'], 'New_admin')
        self.assertEqual(c['email'], 'admin@admin.com')

    def test_empty_search(self):
        self.login()
        context = {'text': 'Filename'}
        response = self.c.post('/search/', context)
        length = 0
        for x in response.context['files_found']:
            length += len(x)
        self.assertEqual(length, 0)

    def test_wrong_search(self):
        self.test_add_new_post()
        context = {'text': 'Filename'}
        response = self.c.post('/search/', context)
        length = 0
        for x in response.context['files_found']:
            length += len(x)
        self.assertEqual(length, 0)

    def test_search(self):
        self.test_add_new_post()
        context = {'text': 'Newfile'}
        response = self.c.post('/search/', context)
        length = 0
        for x in response.context['files_found']:
            length += len(x)
        self.assertEqual(length, 1)

    def test_sign(self):
        self.test_add_new_post()
        self.c.get('/Newfile.pdf/sign/')
        d = Document.objects.get(filename='Newfile.pdf', owner__user__username='Admin')
        self.assertEqual(d.status, 'Готов')
        self.assertEqual(d.signed, 1)

    def test_cancel(self):
        self.test_add_new_post()
        self.c.get('/Newfile.pdf/cancel/')
        d = Document.objects.get(filename='Newfile.pdf', owner__user__username='Admin')
        self.assertEqual(d.status, 'Отменен')
