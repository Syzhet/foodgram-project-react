from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField)
from rest_framework.validators import ValidationError
from users.serializers import CustomUserSerializer

from .addserializers import BaseRecipeDataSerializer
from .models import (Favourites, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag)

ERROR_MESSAGE_FOR_ADD_INGREDIENT = ('Нельзя повторно добавлять '
                                    'ранее добавленный ингредиент')
ERROR_MESSAGE_MIN_VALUE_AMOUNT = ('Количество ингредиента должно '
                                  'быть строго больше нуля')
ERROR_MESSAGE_NO_TAG = 'Необходимо указать хотя бы один тэг'
ERROR_MESSAGE_FOR_ADD_TAG = ('Нельзя повторно добавлять '
                             'ранее добавленный тэг')
ERROR_MESSAGE_MIN_TIME = ('Время приготовления должно быть строго больше нуля')
MIN_VALUE = 0


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
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'text',
            'cooking_time'
        )

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


class AddInRecipeIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(ModelSerializer):

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = AddInRecipeIngredientSerializer(many=True)
    # author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            # 'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate_ingredients(self, value):
        uniq_ingredients = []
        for ingredient in value:
            id_ingredient = ingredient.get('id')
            if id_ingredient in uniq_ingredients:
                raise ValidationError(ERROR_MESSAGE_FOR_ADD_INGREDIENT)
            uniq_ingredients.append(id_ingredient)
            if ingredient.get('amount') <= MIN_VALUE:
                raise ValidationError(ERROR_MESSAGE_MIN_VALUE_AMOUNT)
        return value

    def validate_tags(self, value):
        uniq_tags = []
        if not value:
            raise ValidationError(ERROR_MESSAGE_NO_TAG)
        for tag in value:
            if tag in uniq_tags:
                raise ValidationError(ERROR_MESSAGE_FOR_ADD_TAG)
            uniq_tags.append(tag)
        return value

    def validate_cooking_time(self, value):
        if value <= MIN_VALUE:
            raise ValidationError(ERROR_MESSAGE_MIN_TIME)
        return value

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for tag in tags:
            instance.tags.add(tag)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return super().update(instance, validated_data)


class ShoppingListSerializer(ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return BaseRecipeDataSerializer(instance.recipe, context=context).data
