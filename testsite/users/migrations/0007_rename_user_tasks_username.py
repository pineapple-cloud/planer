# Generated by Django 5.0.4 on 2024-04-18 20:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_tasks_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tasks',
            old_name='user',
            new_name='username',
        ),
    ]