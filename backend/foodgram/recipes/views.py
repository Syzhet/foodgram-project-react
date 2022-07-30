import csv

from django.http import HttpResponse
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.pagination import CustomLimitPaginator

from .filters import RecipeFilter
from .models import (Favourites, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag)
from .permissions import AuthorOrAuthOrRead
from .serializers import (FavouritesSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingListSerializer, TagSerializer)

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

    @staticmethod
    def create_method(request, pk, model, message_exist, serializer):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                ERROR_MESSAGE_NOT_RECIPE,
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {'user': request.user.id, 'recipe': pk}
        if model.objects.filter(**data).exists():
            return Response(
                message_exist,
                status=status.HTTP_400_BAD_REQUEST
            )
        context = {'request': request}
        serializer = serializer(data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete_method(request, pk, model, message):
        user = request.user
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                ERROR_MESSAGE_NOT_RECIPE,
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(id=pk)
        obj = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            message,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        serializer_class=FavouritesSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.create_method(
            request,
            pk,
            Favourites,
            ERROR_MESSAGE_FAVOR_EXISTS,
            self.serializer_class
        )

    @favorite.mapping.delete
    def delete_favoutite(self, request, pk):
        return self.delete_method(
            request,
            pk,
            Favourites,
            ERROR_MESSAGE_NO_FAVOR
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shoppinglist__user=request.user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        )
        shoplist = {}
        for ingredient in ingredients:
            if ingredient[0] in shoplist:
                shoplist[ingredient[0]]['amount'] += ingredient[2]
            else:
                shoplist[ingredient[0]] = {
                    'measurement_unit': ingredient[1],
                    'amount': ingredient[2]
                }
        response = HttpResponse(
            content_type='text/csv',
        )
        writer = csv.writer(response)
        writer.writerow(['number', 'name', 'measurement_unit', 'amount'])
        number = 1
        for name, meas_amount in shoplist.items():
            writer.writerow(
                [
                    f'{number}', f'{name}',
                    f'{meas_amount["measurement_unit"]}',
                    f'{meas_amount["amount"]}'
                ]
            )
            number += 1
        return response

    @action(
        detail=True,
        methods=['post'],
        serializer_class=ShoppingListSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.create_method(
            request,
            pk,
            ShoppingList,
            ERROR_MESSAGE_SHOP_EXISTS,
            self.serializer_class
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method(
            request,
            pk,
            ShoppingList,
            ERROR_MESSAGE_NO_SHOP_CART
        )
