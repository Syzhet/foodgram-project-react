from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
    ModelViewSet,
)
from rest_framework.permissions import AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from .models import (
    Tag,
    Ingredient,
    Recipe,
    Favourites,
    ShoppingList
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    FavouritesSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    ShoppingListSerializer
)
from users.pagination import CustomLimitPaginator
from .permissions import AuthorOrAuthOrRead
from .filters import RecipeFilter


ERROR_MESSAGE_NOT_RECIPE = 'errors: Такого рецепта не существует'
ERROR_MESSAGE_FAVOR_EXISTS = 'errors: Рецепт уже добавлен в избранное'
ERROR_MESSAGE_NO_FAVOR = 'errors: Данного рецепта нет в избранном'
ERROR_MESSAGE_SHOP_EXISTS = 'errors: Рецепт уже добавлен  в список'
ERROR_MESSAGE_NO_SHOP_CART = 'errors: Данного рецепта нет в списке покупок'


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
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrAuthOrRead]
    filterset_class = RecipeFilter
    pagination_class = CustomLimitPaginator

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post'],
        serializer_class=FavouritesSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                ERROR_MESSAGE_NOT_RECIPE,
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {'user': request.user.id, 'recipe': pk}
        if Favourites.objects.filter(**data).exists():
            return Response(
                ERROR_MESSAGE_FAVOR_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_favoutite(self, request, pk):
        user = request.user
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                ERROR_MESSAGE_NOT_RECIPE,
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(id=pk)
        favour = Favourites.objects.filter(
            user=user,
            recipe=recipe
        )
        if favour.exists():
            favour.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            ERROR_MESSAGE_NO_FAVOR,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        serializer_class=ShoppingListSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                ERROR_MESSAGE_NOT_RECIPE,
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {'user': request.user.id, 'recipe': pk}
        if ShoppingList.objects.filter(**data).exists():
            return Response(
                ERROR_MESSAGE_SHOP_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                ERROR_MESSAGE_NOT_RECIPE,
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(id=pk)
        shopping_cart = ShoppingList.objects.filter(
            user=user,
            recipe=recipe
        )
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            ERROR_MESSAGE_NO_FAVOR,
            status=status.HTTP_400_BAD_REQUEST
        )
