from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Create your models here


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notifications = models.TextField()
    personal_files = models.TextField()
    files_to_contrib = models.TextField()


class Document(models.Model):
    filename = models.CharField(max_length=200)
    filepath = models.FilePathField(path=settings.MEDIA_ROOT, null=True)
    date = models.DateField()
    users = models.TextField()
    description = models.TextField(null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
