from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from datetime import date, datetime, timedelta


# Create your models here


class Document(models.Model):
    filename = models.CharField(max_length=200)
    filepath = models.FilePathField(path=settings.MEDIA_ROOT, null=True)
    date = models.DateField()
    description = models.TextField(null=True)
    signs_number = models.PositiveIntegerField(default=0)
    signed = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=25, default='В процессе')

    def __str__(self):
        return self.filename


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notifications = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    personal_files = models.ManyToManyField(Document, related_name='owner', blank=True)
    files_to_contrib = models.ManyToManyField(Document, related_name='reviewer', blank=True)

    def __str__(self):
        return str(self.user)

    def get_statistic(self):
        deadlines_count = 0
        personal_files = Document.objects.filter(owner__user__username=self.user.username)
        if not personal_files:
            personal_files = ''
        files_to_contrib = Document.objects.filter(reviewer__user__username=self.user.username). \
            filter(status='В процессе')
        if files_to_contrib:
            for document in files_to_contrib:
                deadline = date.fromisoformat(str(document.date))
                if deadline - datetime.now().date() <= timedelta(days=1) and document.status != 'Готов':
                    deadlines_count += 1
        else:
            files_to_contrib = ''
        personal_context = {
                'deadlines': deadlines_count,
                'files_to_sign': len(files_to_contrib),
                'personal_files': len(personal_files),
                'my_files': personal_files,
                'review_files': files_to_contrib
                            }
        return personal_context

    def get_group_persons(self):
        persons = set()
        for group in self.user.groups.all():
            users = User.objects.filter(groups=Group.objects.get(name=group.name))
            for user in users:
                persons.add(user.username)
        return persons

    def get_notifications(self):
        notifications = str(self.notifications).split('\n')
        if notifications.count('') != 0:
            notifications.remove('')
        self.notifications = ''
        self.save()
        return notifications

    def update(self, username=None, email=None, password=None):
        if username:
            self.user.username = username
        if email:
            self.user.email = email
        if password:
            self.user.set_password(password)
        self.user.save()


class DiscussionText(models.Model):
    author = models.CharField(max_length=200)
    description = models.TextField()
    publish_date = models.DateField()
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
