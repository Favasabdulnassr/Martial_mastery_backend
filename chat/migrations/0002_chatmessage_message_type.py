# Generated by Django 5.1.4 on 2025-03-24 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='message_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
