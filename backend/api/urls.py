from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RedirectToRecipeAPI, RecipeViewSet,
                       ShoppingCartViewSet, ShoppingCartDownloadView,
                       TagViewSet, FavoriteViewSet)
from users.views import NewUserViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'tags', TagViewSet)
v1_router.register(r'ingredients', IngredientViewSet)
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'users', NewUserViewSet, basename='user')

# v1_router.register(r'recipes/(?P<recipe_id>\d+)/get-link')

v1_router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                   ShoppingCartViewSet, basename='shopping_cart')
v1_router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                   FavoriteViewSet, basename='favorite')


urlpatterns = [
    path('', include(v1_router.urls)),
    path('users/me/', NewUserViewSet.as_view({'get': 'retrieve'}),
         name='user-me'),
    path('recipes/download_shopping_cart/',
         ShoppingCartDownloadView.as_view(), name='download'),
    path('<str:short_link>/', RedirectToRecipeAPI.as_view(),
         name='redirect_to_recipe'),
]
