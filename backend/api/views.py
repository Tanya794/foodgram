from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView

from api.serializers import (IngredientSerializer, RecipeReadSerializer,
                             RecipeIWriteSerializer, TagSerializer)
from recipes.models import Ingredient, Recipe, ShoppingCart, Tag
from recipes.renderers import PlainTextRenderer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """list() и retrieve() для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """list() и retrieve() для модели Ingridient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class ShoppingCartDownloadView(APIView):
    renderer_classes = [PlainTextRenderer]
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        cart_items = ShoppingCart.objects.filter(user=request.user)

        in_cart = {}

        for item in cart_items:
            recipe = item.recipe

            ingredients = recipe.recipe_ingredients.all()

            for ingredient in ingredients:
                ingredient_name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount

                in_cart[(ingredient_name, measurement_unit)] = in_cart.get(
                    (ingredient_name, measurement_unit), 0) + amount

        cart = [f'{key[0]} - {value}({key[1]})' for key, value in
                in_cart.items()]
        content = '\n'.join(cart)

        response = Response(content)
        response['Content-Disposition'] = (
            'attachment; filename="products_list.txt"')

        return response


class RedirectToRecipeAPI(APIView):
    """Перенаправляет по короткой ссылке на рецепт."""

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect('recipe_detail', pk=recipe.id)


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD для модели Recipe."""

    queryset = Recipe.objects.all()

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(reverse('redirect_to_recipe',
                                                args=[recipe.short_link]))
        return Response({'short_link': short_link})

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeIWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
