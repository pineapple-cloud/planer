# Generated by Django 5.0.4 on 2024-04-18 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_tasks_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tasks',
            name='username',
        ),
    ]