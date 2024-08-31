from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.views import ReturnShortLinkRecipeAPI
from users.views import NewUserViewSet


urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('djoser.urls')),

    path('<str:short_link>/', ReturnShortLinkRecipeAPI.as_view(),
         name='recipe-short-link'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
