from django_filters.rest_framework import (
    FilterSet,
    BooleanFilter,
    AllValuesMultipleFilter
)

from .models import Recipe


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(
        method="filter_is_favorited"
    )
    is_in_shopping_cart = BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favourites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(carts__user=self.request.user)
        return queryset
