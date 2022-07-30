from django.contrib import admin

from .models import (Favourites, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag, TagRecipe)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    list_filter = ('slug',)
    list_display_links = ('id', 'slug')
    search_fields = ('id', 'name')
    ordering = ('id', 'slug')
    prepopulated_fields = {"slug": ("name", )}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name',)
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('id', 'name')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'pub_date', 'count_in_favourites')
    fieldsets = (
        ('Основные данные рецепта', {'fields': (
            'name', ('author', 'pub_date'), 'image', 'text', 'cooking_time'
        )}),
        ('Добавления в избранное', {'fields': ('count_in_favourites',)})
    )
    list_filter = ('author', 'name', 'tags')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'author')
    ordering = ('id', 'pub_date', 'name')
    readonly_fields = ('count_in_favourites', 'pub_date')

    @staticmethod
    def count_in_favourites(obj):
        return obj.favourites.count()


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'recipe')
    list_filter = ('recipe',)
    list_display_links = ('id', 'recipe')
    search_fields = ('id', 'recipe', 'tag')
    ordering = ('id',)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    list_filter = ('recipe',)
    list_display_links = ('id', 'recipe')
    search_fields = ('id', 'recipe')
    ordering = ('id',)


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    list_display_links = ('id', 'user')
    search_fields = ('id', 'user', 'recipe')
    ordering = ('user',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    list_display_links = ('id', 'user')
    search_fields = ('id', 'user', 'recipe')
    ordering = ('user',)
