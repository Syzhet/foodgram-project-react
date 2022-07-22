from django.contrib.admin import register, ModelAdmin

from .models import Tag, Ingredient


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    list_filter = ('slug'),
    list_display_links = ('id', 'slug')
    search_fields = ('id', 'name')
    ordering = ('id', 'slug')


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name'),
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('id', 'name')
