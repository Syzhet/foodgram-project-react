from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username,
        first_name,
        last_name,
        password,
        **extra_fields
    ):
        if not username:
            raise ValueError('Юзернейм не может быть пустым!')
        if not email:
            raise ValueError('Почта не может быть пустой!')
        if not first_name:
            raise ValueError('Юзернейм не может быть пустым!')
        if not last_name:
            raise ValueError('Юзернейм не может быть пустым!')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.password = make_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        email,
        username,
        first_name,
        last_name,
        password,
        **extra_fields
    ):
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_superuser'):
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True!'
            )
        return self.create_user(
            email,
            username,
            first_name,
            last_name,
            password,
            **extra_fields
        )
