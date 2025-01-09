# Generated by Django 5.1.3 on 2024-12-29 10:43

import cloudinary_storage.storage
import cloudinary_storage.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tutorials', '0003_alter_video_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_file',
            field=models.FileField(blank=True, null=True, storage=cloudinary_storage.storage.VideoMediaCloudinaryStorage(), upload_to='tutorial_videos/', validators=[cloudinary_storage.validators.validate_video]),
        ),
    ]
