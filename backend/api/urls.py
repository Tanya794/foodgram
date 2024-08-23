from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RedirectToRecipeAPI, RecipeViewSet,
                       ShoppingCartDownloadView, TagViewSet)

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'tags', TagViewSet)
v1_router.register(r'ingredients', IngredientViewSet)
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')

# v1_router.register(r'recipes/(?P<recipe_id>\d+)/get-link')

#v1_router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart')
#v1_router.register(r'recipes/(?P<recipe_id>\d+)/favorite')


urlpatterns = [
    path('', include(v1_router.urls)),
    path('recipes/download_shopping_cart/',
         ShoppingCartDownloadView.as_view(), name='download'),
    path('<str:short_link>/', RedirectToRecipeAPI.as_view(),
         name='redirect_to_recipe'),
]
