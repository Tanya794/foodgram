from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
                       ShoppingCartDownloadView, SubscriptionListAPI,
                       TagViewSet, FavoriteViewSet)
from users.views import NewUserViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'tags', TagViewSet)
v1_router.register(r'ingredients', IngredientViewSet)
v1_router.register(r'recipes', RecipeViewSet, basename='recipe')


# v1_router.register(r'recipes/(?P<recipe_id>\d+)/get-link')

# v1_router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#                   ShoppingCartViewSet, basename='shopping_cart')
# v1_router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
#                   FavoriteViewSet, basename='favorite')


urlpatterns = [
    path('', include(v1_router.urls)),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopping_cart'),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='favorite'),

    path('users/subscriptions/', SubscriptionListAPI.as_view(),
         name='subscriptions'),

    path('users/me/', NewUserViewSet.as_view({'get': 'retrieve'}),
         name='user-me'),

    path('recipes/download_shopping_cart/',
         ShoppingCartDownloadView.as_view(), name='download'),
]
