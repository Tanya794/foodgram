import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Ingredient, IngredientRecipe, Favorite,
                            Recipe, ShoppingCart, Tag, TagRecipe)
from users.serializers import NewUserSerializer


class Base64ImageField(serializers.ImageField):
    """Декодирует изображение из base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = NewUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,
                                           recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            if 'request' in self.context:
                representation['image'] = self.context[
                    'request'].build_absolute_uri(instance.image.url)
            else:
                representation['image'] = instance.image.url
        return representation


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи игредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeIWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи модели рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_empty=False,
        allow_null=False
    )
    image = Base64ImageField()
    ingredients = IngredientRecipeWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients_data:
            cur_ingredient = Ingredient.objects.get(id=ingredient['id'])
            IngredientRecipe.objects.create(recipe=recipe,
                                            ingredient=cur_ingredient,
                                            amount=ingredient['amount'])

        for tag in tags_data:
            current_tag = Tag.objects.get(**tag)
            TagRecipe.objects.create(recipe=recipe, tag=current_tag)

        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        instance.tags.set(tags_data)

        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_data:
            cur_ingredient = ingredient['id']
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=cur_ingredient,
                amount=ingredient['amount']
            )

        instance.save()
        return instance

    def to_representation(self, instance):
        """Метод для возвращения данных, как при GET запросе."""
        serializer = RecipeReadSerializer(instance)
        return serializer.data
