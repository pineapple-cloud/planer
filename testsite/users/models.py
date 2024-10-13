from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        unique=True
    )
    email_verify = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Tasks(models.Model):
    objects = None
    title = models.CharField(max_length=255, verbose_name='Название задачи')
    content = models.TextField(blank=True, verbose_name='Дополнительная информация', max_length=1024)
    day_to_do = models.DateField(verbose_name='Дедлайн')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    done = models.BooleanField(default=False, verbose_name='В архив')
    tag = models.TextField(blank=True, verbose_name='Тэг', max_length=255)
    urgent = models.BooleanField(default=False, verbose_name='Срочно')
    important = models.BooleanField(default=False, verbose_name='Важно')
    username = models.TextField(blank=True)
