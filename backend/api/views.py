from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView

from api.serializers import IngredientSerializer, TagSerializer
from recipes.models import Ingredient, ShoppingCart, Tag
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
