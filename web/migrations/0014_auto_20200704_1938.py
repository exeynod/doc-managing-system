# Generated by Django 3.0.3 on 2020-07-04 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_auto_20200704_1925'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='approved',
        ),
        migrations.AddField(
            model_name='profile',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
