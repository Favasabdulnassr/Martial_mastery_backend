# Generated by Django 5.1.3 on 2025-01-06 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0007_alter_customuser_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, default=None, max_length=15, null=True, unique=True),
        ),
    ]
