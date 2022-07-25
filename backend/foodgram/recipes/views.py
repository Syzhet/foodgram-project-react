from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework import filters

from .models import (
    Tag,
    Ingredient,
    Recipe,
    TagRecipe,
    IngredientRecipe,
    Favourites,
    ShoppingList
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)