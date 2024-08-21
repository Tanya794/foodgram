from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, ShoppingCartDownloadView, TagViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'tags', TagViewSet)
v1_router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(v1_router.urls)),
    path('recipes/download_shopping_cart/',
         ShoppingCartDownloadView.as_view(), name='download'),
]
