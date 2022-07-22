from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone

from .managers import UserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('Логин', max_length=150, unique=True)
    email = models.EmailField('Электронная почта', unique=True)
    password = models.CharField('Пароль', max_length=100)
    first_name = models.CharField(
        'Имя пользователя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=150
    )
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_blocked = models.BooleanField('Заблокирован', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    EMAIL_FIELD = 'email'

    objects = UserManager()

    class Meta:
        ordering = ['-pk', ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser


class SubscribeModel(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='author'
    )
    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'follower'],
                name='unique_subsscribe',
            )
        ]
