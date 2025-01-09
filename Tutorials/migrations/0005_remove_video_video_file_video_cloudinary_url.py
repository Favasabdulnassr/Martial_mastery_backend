# Generated by Django 5.1.3 on 2024-12-29 11:33

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Tutorials', '0004_alter_video_video_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='video_file',
        ),
        migrations.AddField(
            model_name='video',
            name='cloudinary_url',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='video'),
        ),
    ]
