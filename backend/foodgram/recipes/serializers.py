from rest_framework.validators import ValidationError
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    ReadOnlyField
)


from users.serializers import CustomUserSerializer

from .models import (
    Tag,
    Ingredient,
    Recipe,
    TagRecipe,
    IngredientRecipe,
    Favourites,
    ShoppingList
)
from .addserializers import BaseRecipeDataSerializer


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ('__all__',)


class FavouritesSerializer(ModelSerializer):

    class Meta:
        model = Favourites
        fields = ('recipe', 'user')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = data.get('recipe')
        favour = Favourites.objects.filter(user=user, recipe=recipe).exists()
        if favour:
            raise ValidationError('Этот рецепт уже добавлен в избранное')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return BaseRecipeDataSerializer(instance.recipe, context=context).data


class IngredientRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favourites.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj).exists()
