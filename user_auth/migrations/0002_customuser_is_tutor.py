# Generated by Django 5.1.3 on 2024-11-16 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_tutor',
            field=models.BooleanField(default=True),
        ),
    ]
