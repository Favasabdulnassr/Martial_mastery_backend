# Generated by Django 5.1.4 on 2025-02-05 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Courses', '0002_alter_courselesson_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courselesson',
            name='order',
            field=models.PositiveIntegerField(),
        ),
    ]
