from django.db import models


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=50, unique=True)
    color = models.CharField('Цвет тега', max_length=7)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingridient_and_measurement')
        ]
