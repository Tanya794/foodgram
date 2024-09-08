from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from django.urls import NoReverseMatch, reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserSerializer
from djoser.views import UserViewSet
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, SAFE_METHODS,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FoodgramPagination
from api.permissions import ActionRestriction, IsAuthorOrStaff
from api.serializers import (AvatarSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeIWriteSerializer,
                             RecipeReadSerializer, ShoppingCartSerializer,
                             SubscribeActionSerializer, TagSerializer,
                             NewUserSerializer, UserCreateSerializer)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from recipes.renderers import PlainTextRenderer
from users.models import Subscription


User = get_user_model()


class NewUserViewSet(UserViewSet):
    """Переопределяет вьюсет пользователя от djoser."""

    serializer_class = NewUserSerializer
    permission_classes = (ActionRestriction, IsAuthenticated)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class UserGetViewSet(viewsets.ViewSet):
    """Предоставляет просмотр и создание юзера(ов)."""

    permission_classes = (AllowAny,)

    def list(self, request):
        queryset = User.objects.order_by('id')
        paginator = FoodgramPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = NewUserSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = NewUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = UserSerializer(user)
        return Response(response_serializer.data,
                        status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """list() и retrieve() для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """list() и retrieve() для модели Ingridient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class ShoppingCartDownloadView(APIView):
    """Скачивание списка покупок."""

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
    """Перенаправляет на объект рецепта по короткой ссылке."""

    permission_classes = (ActionRestriction,)

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        recipe_id = recipe.id
        recipe_url = f'{settings.BASE_URL}/recipes/{recipe_id}/'
        return redirect(recipe_url)


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD для модели Recipe."""

    permission_classes = (IsAuthorOrStaff,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated \
            else None
        return Recipe.objects.prefetch_related(
            'ingredients', 'tags'
        ).select_related('author').annotate(
            is_favorited=Exists(Favorite.objects.filter(
                user=user, recipe=OuterRef('pk'))),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                user=user, recipe=OuterRef('pk')))
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Получение короткой ссылки к рецепту."""
        recipe = self.get_object()
        try:
            short_link = request.build_absolute_uri(reverse(
                'recipe-short-link', args=[recipe.short_link]))
        except NoReverseMatch:
            return Response({'detail': 'Маршрут не найден'}, status=404)

        return Response({'short-link': short_link})

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
                            status=status.HTTP_400_BAD_REQUEST)


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
                            status=status.HTTP_400_BAD_REQUEST)


class SubscriptionListAPI(generics.ListAPIView):
    """Получение списка подписок текущего юзера."""

    serializer_class = SubscribeActionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        current_user = self.request.user
        return current_user.subscriptions.all().order_by('id')


class SubscribeViewSet(viewsets.ViewSet):
    """Подписаться / отписаться от кого-то."""

    permission_classes = (IsAuthenticated,)

    def create(self, request, user_id):
        subscrited_to = get_object_or_404(User, id=user_id)
        print(f'{subscrited_to}')
        serializer = SubscribeActionSerializer(
            data={'subscribed_to': subscrited_to.id},
            context={'request': request}
        )

        if serializer.is_valid():
            pair = serializer.save()
            return Response(SubscribeActionSerializer(pair).data,
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        try:
            pair = Subscription.objects.get(user=request.user,
                                            subscribed_to=user)
            pair.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Subscription.DoesNotExist:
            return Response({"detail": "Пользователь не найден."},
                            status=status.HTTP_404_NOT_FOUND)


class AvatarUpdateView(generics.UpdateAPIView):
    """Обновление / удаление аватара."""

    queryset = User.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
