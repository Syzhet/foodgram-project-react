from django.db import models
from django.core import validators

from users.models import CustomUser


MIN_TIME_LIMIT = 'Время приготовления не может быть меньше 1-й минуты'
VALUE_MIN_TIME_LIMIT = 1


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=50, unique=True)
    color = models.CharField('Цвет тега', max_length=7)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='tags_for_recipe',
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingridients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='ingridients_for_recipe',
        verbose_name='Ингредиенты'
    )
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField(
        'Изображение бллюда',
        upload_to='recipes/%Y/%m/%d/'
    )
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления блюда',
        validators=[validators.MinValueValidator(
            limit_value=VALUE_MIN_TIME_LIMIT,
            message=MIN_TIME_LIMIT
            )
        ]
    )


# Дописать связные таблицы для Тэгов и для Ингредиентов