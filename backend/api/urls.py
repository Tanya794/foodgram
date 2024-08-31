from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
                       ShoppingCartDownloadView, SubscriptionListAPI,
                       TagViewSet, FavoriteViewSet, SubscribeViewSet,
                       AvatarUpdateView)
from users.views import NewUserViewSet, UserGetViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'tags', TagViewSet)
v1_router.register(r'ingredients', IngredientViewSet)
v1_router.register(r'recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('recipes/download_shopping_cart/',
         ShoppingCartDownloadView.as_view(), name='download'),
    path('', include(v1_router.urls)),

    path('users/', UserGetViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='user-list-create'),

    path('users/<int:pk>/', UserGetViewSet.as_view({'get': 'retrieve'}),
         name='user-detail'),

    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopping_cart'),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='favorite'),
    path('users/me/avatar/', AvatarUpdateView.as_view(), name='user-avatar'),
    path('users/subscriptions/', SubscriptionListAPI.as_view(),
         name='subscriptions'),
    path('users/me/', NewUserViewSet.as_view({'get': 'retrieve'}),
         name='user-me'),
    path('users/<int:user_id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='subscribe-to'),
]
