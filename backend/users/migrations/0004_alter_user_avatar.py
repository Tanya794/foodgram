# Generated by Django 3.2.3 on 2024-08-19 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20240819_0559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='users/', verbose_name='Аватар'),
        ),
    ]
