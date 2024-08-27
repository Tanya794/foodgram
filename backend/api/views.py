from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.urls import reverse, NoReverseMatch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeReadSerializer,
                             RecipeIWriteSerializer, ShoppingCartSerializer,
                             TagSerializer, FavoriteSerializer,
                             SubscriptionSerializer)
from recipes.models import Ingredient, Recipe, ShoppingCart, Tag, Favorite
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


class ReturnShortLinkRecipeAPI(APIView):
    """Возвращает объект рецепта по короткой ссылке."""

    permission_classes = (IsAuthorOrReadOnly,)

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        serializer = RecipeReadSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD для модели Recipe."""

    queryset = Recipe.objects.prefetch_related(
        'ingredients', 'tags').select_related('author')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        print('GET LINK')
        recipe = self.get_object()
        try:
            short_link = request.build_absolute_uri(reverse(
                'recipe-short-link', args=[recipe.short_link]))
        except NoReverseMatch:
            return Response({'detail': 'Маршрут не найден'}, status=404)

        return Response({'short_link': short_link})

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeIWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class ShoppingCartViewSet(viewsets.ViewSet):
    """Добавление или удаление рецепта из корзины."""

    permission_classes = (IsAuthenticated,)

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer = ShoppingCartSerializer(data={'recipe': recipe.id},
                                            context={'request': request})

        if serializer.is_valid():
            cart_item = serializer.save()
            return Response(ShoppingCartSerializer(cart_item).data,
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            cart_item = ShoppingCart.objects.get(user=request.user,
                                                 recipe=recipe)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingCart.DoesNotExist:
            return Response({"detail": "Рецепта нет в корзине."},
                            status=status.HTTP_404_NOT_FOUND)


class FavoriteViewSet(viewsets.ViewSet):
    """Добавление или удаление рецепта в Избранное."""

    permission_classes = (IsAuthenticated,)

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer = FavoriteSerializer(data={'recipe': recipe.id},
                                        context={'request': request})

        if serializer.is_valid():
            fav_item = serializer.save()
            return Response(FavoriteSerializer(fav_item).data,
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            fav_item = Favorite.objects.get(user=request.user,
                                            recipe=recipe)
            fav_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({"detail": "Рецепта нет в Избранном."},
                            status=status.HTTP_404_NOT_FOUND)


class SubscriptionListAPI(generics.ListAPIView):
    """Получение списка подписок текущего юзера."""

    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        current_user = self.request.user
        return current_user.subscriptions.all().order_by('id')
