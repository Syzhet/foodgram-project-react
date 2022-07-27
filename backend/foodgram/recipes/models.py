from django.db import models
from django.core import validators
# from django.urls import reverse

from users.models import CustomUser


MIN_TIME_LIMIT = 'Время приготовления не может быть меньше 1-й минуты'
VALUE_MIN_TIME_LIMIT = 1
MIN_AMOUNT_LIMIT = 'Количество ингредиента не может быть мень 1'
VALUE_MIN_AMOUNT_LIMIT = 1


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=50, unique=True)
    color = models.CharField('Цвет тега', max_length=7, unique=True)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('', kwargs={'pk': self.pk})  # здесь необходимо уточнить имя URL


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingridient_and_measurement'
            )
        ]

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('', kwargs={'pk': self.pk})  # здесь необходимо уточнить имя URL


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
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='ingridients_for_recipe',
        verbose_name='Ингредиенты'
    )
    name = models.CharField('Название рецепта', max_length=200)
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True
    )
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

    class Meta:
        ordering = ['-pub_date', 'name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('', kwargs={'pk': self.pk})  # здесь необходимо уточнить имя URL


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэги и рецепты'
        verbose_name_plural = 'Тэги и рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tag_and_recipe'
            )
        ]

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=[validators.MinValueValidator(
            limit_value=VALUE_MIN_AMOUNT_LIMIT,
            message=MIN_AMOUNT_LIMIT
            )
        ]
    )

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name = 'Количество ингредиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingridient_and_recipe'
            ),
        ]


class Favourites(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourites'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppinglist'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
