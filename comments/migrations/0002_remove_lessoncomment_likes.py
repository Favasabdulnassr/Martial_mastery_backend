# Generated by Django 5.1.4 on 2025-01-23 09:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lessoncomment',
            name='likes',
        ),
    ]
